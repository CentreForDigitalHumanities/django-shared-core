let VueUil = {
    install: function (Vue, options) {
        /**
         * This method exposed the window.reverse method to Vue as a instance method
         *
         * Depends on js-urls of uil.core
         * @param url String The name of the url to resolve
         * @param params Any URL parameters needed
         * @returns {*}
         */
        Vue.prototype.$url = function (url, params) {
            // If it's already a resolved URL, just return that
            if(url.startsWith('/') || url.startsWith("http"))
                return url;

            return window.reverse(url, params);
        }

        Vue.prototype.$log = console.log.bind(console)

        Vue.prototype.$ufl_load = function (app, url) {
            $.get(url, data => {
                for (const [key, value] of Object.entries(data)) {
                  app[key] = value;
                }
                app.loaded = true;
            });
        }

        Vue.createFancyList = function (element, template, locale, url, url_args=[]) {
            const i18n = new VueI18n({
                locale: locale,
            });

            return new Vue({
                i18n,
                el: element,
                template: template,
                components: {
                    // Loaded by the load_vue_component tag, no need to manually load this
                    FancyList
                },
                data: function () {
                    return {
                        // Actual data loaded through $ufl_load in mounted()
                        'items': [],
                        // Default to false, as this will make the loading seem more seamless. (Defaults to true in
                        // FancyListApiView anyway, so it will probably be enabled through that).
                        'showControls': false,
                        'context': {},
                        'searchableFields': [],
                        'filterDefinitions': {},
                        'numItemsOptions': [],
                        'defaultItemsPerPage': 10,
                        'sortDefinitions': {},
                        'loaded': false,
                    };
                },
                mounted() {
                    this.$ufl_load(this, this.$url(url, url_args));
                },
            });
        }

        Vue.filter('date', function(timestamp, format="YYYY-MM-DD") {
            if(timestamp == null)
                return ""
            let date = new Date(timestamp);

            return moment(date).format(format)
		});
    }
}

Vue.use(VueUil, {});