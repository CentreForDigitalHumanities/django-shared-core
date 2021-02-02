(function ($) {
    $.widget('uu.fancyList', {
        options: {
            itemsOnPage: {
                options: [5, 10, 25, 50],
                current: 10,
            },
            language: 'en',
            numItems: -1,
            paginationScriptLocation: '/static/uil.core/js/pagination.js',
        },

        _create: function () {
            let self = this;
            this._loadPaginationScript().done(function () {
                self._createControlElements();

                if (self.options.numItems === -1)
                    self.options.numItems = self.element.find('.ufl-item').length;

                self._createPagination();

                self._registerEventCallbacks();
            });
        },

        _loadPaginationScript: function () {
            if (typeof $.fn.pagination !== "function") {
                return $.getScript(this.options.paginationScriptLocation);
            }

            // It's already loaded, return a resolved promise so that execution can proceed
            return $.when();
        },

        _createControlElements: function () {
            let container = $('<div class="uu-fancy-list-controls clearfix"></div>');
            this.element.prepend(container);

            this._createNumItemsControls(this, container);
            this._createSearchControls(this, container);
        },

        _createNumItemsControls: function (self, container) {
            let numItemsContainer = $('<label></label>');

            switch (this.options.language) {
                case 'nl':
                    numItemsContainer.append("Items per pagina: ");
                    break;
                case "en":
                    numItemsContainer.append("Items per page: ");
                    break;
            }

            let numItemsControl = $('<select name="numItems" class="ufl-numItems"></select>');
            self.options.itemsOnPage.options.forEach(function (num) {
                let option = $('<option></option>');
                option.attr('value', num);
                option.html(num);

                if (self.options.itemsOnPage.current === num)
                    option.attr('selected', 'selected');

                numItemsControl.append(option);
            });

            numItemsContainer.append(numItemsControl);
            container.append(numItemsContainer);

            numItemsControl.select2({
                minimumResultsForSearch: Infinity
            });

            numItemsControl.change(function () {
                self.options.itemsOnPage.current = $(this).val();
                self.element.find('.ufl-pagination').pagination(
                    'updateItemsOnPage',
                    self.options.itemsOnPage.current,
                );
                self.resetPaging();
            });
        },

        _createSearchControls: function (self, container) {
            let searchBox = $('<input class="uu-fancy-list-search" />');

            switch (this.options.language) {
                case 'nl':
                    searchBox.attr('placeholder', "Zoeken");
                    break;
                case "en":
                    searchBox.attr('placeholder', "Search");
                    break;
            }

            searchBox.on(
                'keyup change paste',
                function () {
                    let searchVal = $(this).val().toLowerCase();

                    self.element.find('.ufl-item ').each(function (i, el) {
                        let jEl = $(el);
                        let content = jEl.html().toLowerCase();
                        jEl.attr(
                            'data-show',
                            content.indexOf(searchVal) > -1
                        );
                    });

                    self.resetPaging();
                },
            );

            container.append(searchBox);
        },

        _createPagination: function () {
            let self = this;
            let paginationContainer = $('<div class="w-100 ufl-pagination"></div>');

            this.element.append(paginationContainer);

            paginationContainer.pagination({
                items: self.options.numItems,
                itemsOnPage: self.options.itemsOnPage.current,
                prevText: '',
                nextText: '',
                onInit: function () {
                    self.resetPaging();
                },
                onPageClick: function (pageNumber) {
                    self._showPage(pageNumber);
                }
            });
        },

        _registerEventCallbacks: function () {
            let self = this;

            this.element.find(".ufl-item").click(function () {
                let el = $(this);
                if (el.hasClass('expanded')) {
                    el.find('.ufl-details').slideUp();
                    el.removeClass('expanded');
                } else {
                    self.element.find('.ufl-item').each(
                        function (i, item) {
                            let el = $(item);
                            el.find('.ufl-details').slideUp();
                            el.removeClass('expanded');
                        }
                    )
                    el.find('.ufl-details').slideDown();
                    el.addClass('expanded');
                }

            });

            this.element.find('.ufl-item a').click(function (event) {
                // Stop links in .ufl-item triggering the .ufl-item events
                event.stopPropagation();
            });
        },

        _showPage: function (pageNumber) {
            this.element.find('.ufl-item').hide();
            this.element.find(`.ufl-item[data-page=${pageNumber}]`).show()
        },

        _setPageNumberAttr: function () {
            let self = this;

            this.element.find('.ufl-item').each(
                (i, el) => $(el).removeAttr('data-page')
            );

            let visibleItems = this.element.find('.ufl-item[data-show="true"]');
            visibleItems.each(function (i, el) {
                let pagenr = Math.floor(i / self.options.itemsOnPage.current) + 1;
                $(el).attr('data-page', pagenr);
            });
            this.element.find('.ufl-pagination').pagination(
                'updateItems',
                visibleItems.length
            );
        },

        resetPaging: function () {
            $("#ufl-no-items").remove();
            this._setPageNumberAttr();
            this._showPage(1);

            let visibleItems = this.element.find('.ufl-item[data-show="true"]');
            if (visibleItems.length === 0) {
                let warning = $('<div class="info" id="ufl-no-items"></div>');

                switch(this.options.language) {
                    case "nl":
                        warning.html("Er zijn geen items om weer te geven.")
                        break;
                    case "en":
                        warning.html("There are no items to display");
                        break;
                }

                this.element.find('.uu-fancy-list').append(warning);
            }
        }
    });
})(jQuery);