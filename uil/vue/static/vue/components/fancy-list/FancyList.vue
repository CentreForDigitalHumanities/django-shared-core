<!--
UiL Fancy List
UFL is a DataTables replacement, which allows for a more visually pleasing and
(more importantly) readable list view.

(Till otherwise stated, this should all go into the <head> tag of your page)
To use, one can load it into your django view with the following tag:
    {% load vue_tags %}
    {% load_vue_component 'FancyList' %}

Make sure Vue is loaded beforehand:
    {% include 'uil.vue/vueloader.html' %}

You'll also need to include a template for your list:
<script type="text/x-template" id="xList">
    <FancyList
            {% include 'uil.vue/fancy-list-params.txt' %}
    >
        <template #title="{ item, context }">

        </template>
        <template #actions="{ item, context }">

        </template>
        <template #undertitle="{ item, context }">

        </template>
        <template #details="{ item, context }">

        </template>
    </FancyList>
</script>

Each template in the FancyList element corresponds to a part of a list item:
- Title:      First line of the list. Should wrap contents in a h4.
- Actions:    A number of actions for that element. Must be images only
              (wrapped in a link). Will be displayed after the title on
              desktops. Below it on mobile. This template is the only optional
              template.
- Undertitle: Second line. Should display a couple of attributes that should be
              visible at a glance. Should also wrap each attribute in a
              <div class="ufl-undertitle-line"> for proper separation of
              attributes on both desktop and mobile.
- Details:    Everything that will be displayed when an item is 'expanded'.
              Should contain all data that isn't needed at a glance. It's placed
              in a div, which can contain anything. Go nuts.

The item variable will be filled for each list item with the corresponding data
of said item. The context variable will be filled with the same data for all
items, which will be taken from the context attribute of FancyList. (If you use
the FancyListApiView, this is where data from get_context() ends up).

Add an empty div in your body where you want your list to appear. Set an unique
id on that div.

Lastly, add the following JS at the end of your HTML head tag:
window.onload = _ => {
    Vue.createFancyList(div, template, language, url);
}
Where:
- div:      the id of the element you just created in your body (with a leading
            '#')
- template: the id of your template (with a leading '#')
- language: a language code that corresponds to the current language of the site
            This can be retrieved as so:
            {% load i18n %}
            {% get_current_language as LANGUAGE_CODE %}

- url:      the place where the data can be retrieved. You can use the django
            URL format (eg app:view)
            It's recommended to use FancyListApiView as the view, as that
            already serves the data in the right format.

Example:
window.onload = _ => {
    Vue.createFancyList(
        "#list",
        "#decisionList",
        '{{ LANGUAGE_CODE }}',
        'reviews:decisions_api'
    );
}

-->
<template>
  <div class="ufl-container">
    <Controls
      v-model:value="controlValues"
      :num-items-options="numItemsOptions"
      :available-filters="availableFilters"
      :available-sort-options="availableSortOptions"
      @filterChange="filterChange"
    ></Controls>

    <div class="info mt-3" id="ufl-no-items" v-if="!visibleItems.length && loaded">
      {{ $t('no_items') }}
    </div>

    <div class="info mt-3" id="ufl-loading" v-if="!loaded">
      {{ $t('loading') }}
    </div>

    <ListContainer
      :items="visibleItems"
      :context="context"
    >
      <!-- Pass all slots to ListContainer
      This way, we can define the template of ListItem all the way up in the
      root template -->
      <template
          v-for="(_, name) in $scopedSlots"
          :slot="name"
          slot-scope="slotData"
      >
        <slot :name="name" v-bind="slotData" />
      </template>
    </ListContainer>

    <Pagination
        :num-items="filteredItems.length"
        :items-per-page="controlValues.itemsPerPage"
        :page="page"
        @switchToPage="page = $event"
    ></Pagination>

  </div>
</template>

<script>
import Controls from './subcomponents/Controls.vue'
import Pagination from "./subcomponents/Pagination.vue";
import ListContainer from "./subcomponents/ListContainer.vue";

export default {
  name: "FancyList",
	components: {
		Controls, Pagination, ListContainer
	},
  props: {
    // Array of objects. This object should contain data to be used in the item
    // template
    // An individual item will be added to the template slots under the `item`
    // attribute
    items: {
      type: Array,
      required: true,
    },
    // An array of all fields that search should search through
    // Must be an array of pathstrings
    // Can be left out or set to null, in which case all fields in an item is
    // searchable
    searchableFields: {
      type: Array,
      required: false,
      default: undefined,
    },
    // Dictionary of sort definitions. Keys should be the pathstring
    // corresponding to the field that can be sorted on
    //
    // Values should be a dict with the following fields:
    // label: String to be displayed in the select box. Up/down arrows are
    //        automatically added
    // asc: Bool, true if this field should be sortable ascending
    // desc: Bool, true if this field should be sortable descending
    // default: 'asc'|'desc'|null. If not null, this field and direction will be
    //          the default sort on load.
    sortDefinitions: {
      type: Object,
      default() { return {} }
    },
    // Array of allowed values for items per page
    numItemsOptions: {
      type: Array,
      default() { return [5, 10, 25, 50] },
    },
    // Dictionary of filter definitions. Keys should be the pathstring
    // corresponding to the field that can be filtered on Value should be a
    // human readable version of the field, for display  purposes
    // Possible filter options are automatically calculated from the provided
    // items
    filterDefinitions: {
      type: Object,
      default() { return {} }
    },
    // Dictionary of any values that every item should have access to
    // Provided to the item slots under the `context` attribute
    context: {
      type: Object,
      default() { return {} },
    },
    // Set to true if data is loaded
    // If false, will display a message that the data is loading
    loaded: {
      type: Boolean,
      default: false,
    }
  },
  data () {
    return {
      // All values that Control can handle using v-model
      controlValues: {
        search: "",
        itemsPerPage: 10,
        sortOn: undefined,
      },
      // Which page we're on
      page: 1,
      // Any applied filters. Set in Controls.vue, updated here through the
      // filterChange method
      filters: {},
      // List of all fields that we can search through. Either taken from the
      // searchableFields prop, or automatically generated upon load
      searchFields: [],
    }
  },
  i18n: {
    messages: {
      en: {
        no_items: "There are no items to display",
        loading: "Loading items",
      },
      nl: {
        no_items: "Er zijn geen items om weer te geven",
        loading: "Items worden geladen",
      }
    }
  },
  computed: {
    /**
     * This method takes all items, and returns a subset of items that pass all
     * filters. (Search counts as a filter here)
     * It will also sort them if needed.
     * @returns {*[]}
     */
    filteredItems() {
      let items = this.items.filter(item => {
        for (const filter of Object.keys(this.filters)) {
          let allowed_values = this.filters[filter];

          // If this filter was registered but has no allowed values, we ignore
          // this filter.
          if (allowed_values.length === 0)
            continue;

          let value = this.getValFromPathstring(filter, item);

          if (!allowed_values.includes(value)) {
            return false;
          }
        }

        if (this.controlValues.search) {
          let found = false;
          for (const field of this.searchFields) {
            let value = this.getValFromPathstring(field, item);

            if (String(value).toLowerCase().includes(this.controlValues.search)) {
              found = true;
              break; // No sense continuing, as we know this item is to be
                     // included
            }
          }

          return found;
        }

        return true;
      });

      if(this.controlValues.sortOn) {
        // We split the sortOn on the last period, as that part contains
        // whether we should sort ascendingly or descendingly
        let lastIndex = this.controlValues.sortOn.lastIndexOf('.');
        let field = this.controlValues.sortOn.substr(0, lastIndex);
        // The + 1 makes sure we don't include the period
        let direction = this.controlValues.sortOn.substr(lastIndex + 1);

        items = items.sort((a, b) => {
          let valueA = this.getValFromPathstring(field, a);
          let valueB = this.getValFromPathstring(field, b);

          if (direction === 'asc') {
            return (valueA > valueB) ? 1 : -1;
          }

          return (valueA < valueB) ? 1 : -1;
        });
      }

      return items;
    },

    /**
     * This method takes the filtered items, and slice out a part for the
     * current page.
     * @returns {*[]}
     */
    visibleItems() {
      return this.filteredItems.slice(
          (this.page - 1) * this.controlValues.itemsPerPage,
          this.page * this.controlValues.itemsPerPage
      );
    },

    /**
     * This method takes all filter definitions, and finds all possible options
     * for those filters.
     * This is done by simply iterating over every item, and add it's value for
     * the field to a set.
     * @returns {[]}
     */
    availableFilters() {
      let options = [];

      for (const [field, display_name] of Object.entries(this.filterDefinitions)) {
        let option = {
          key: field,
          display: display_name,
          options: new Set(),
        }
        this.items.forEach(item => {
          option.options.add(this.getValFromPathstring(field, item));
        });
        options.push(option);
      }

      return options;
    },

    /**
     * This method generates an array that Controls can understand to define
     * sort options from the sort definitions
     * @returns {[]}
     */
    availableSortOptions() {
      let options = [];

      for(const [field, defs] of Object.entries(this.sortDefinitions)) {
        if(defs.asc)
          options.push({
            key: field + '.asc',
            label: defs.label + ' ↑',
          });
        if(defs.desc)
          options.push({
            key: field + '.desc',
            label: defs.label + ' ↓',
          });
      }

      return options;
    }
  },
  methods: {
    /**
     * Event handler to set a filter's new value
     * @param data Object containing the filter key, and the new allowed values
     */
    filterChange(data) {
      // Use Vue methods to set, as this will trigger any computed var that uses
      // this to refresh
      // In other words, using the native set will not update the list of
      // filtered items properly, but this will
      this.$set(this.filters, data.key, data.value);
    },

    /**
     * Helper function to get a value from an object using a path string.
     * A path string is a string, roughly corresponding to how you would access
     * (nested) properties of an object. (Sans the object's name itself).
     *
     * This solves the problem of trying to access a nested property of an
     * object dynamically. By default, you can only reference an attribute
     * dynamically one layer deep (obj[x]). This method does some magic
     * to allow you to dig deeper!
     *
     * Example:
     * let example = {
     *   a: {
     *     b: "Hello world"
     *   },
     *   c: "Goodbye cruel world!",
     *   d: {
     *     e: {
     *       f: "I like trains",
     *     }
     *   }
     * }
     *
     * this.$getValFromPathstring('a', example)
     * > {
     * >   b: "Hello world"
     * > }
     *
     * this.$getValFromPathstring('d.e.f', example)
     * > "I like trains"
     *
     * @param pathstring
     * @param object
     * @returns {*}
     */
    getValFromPathstring(pathstring, object) {
      return pathstring.split('.').reduce(function(m, n){ return m[n] }, object)
    }
  },
  watch: {
    'controlValues.itemsPerPage': function () {
      // Reset to page one if we change page sizes.
      this.page = 1;
    },
    filters () {
      // Reset to page one if a filter changes
      this.page = 1
    },
    /**
     * Our sort defintions only really change when they're loaded,
     * so we watch for that load to set the default sort
     */
    sortDefinitions() {
      for (const [field, defs] of Object.entries(this.sortDefinitions)) {
        if (defs.default) {
          this.controlValues.sortOn = field + '.' + defs.default;
          break;
        }
      }
    },
    /**
     * Sets the fields we are allowed to search upon items load.
     * We do this on item load, as often we need to generate these fields from
     * the items
     */
    items() {
      // If no custom searchable fields are set, we generate a list ourselves
      if(typeof this.searchableFields === "undefined" ||
         this.searchableFields.length === 0
      ) {
        // Recursive helper to get all fields
        let getFields = (node) => {
          let fields = [];
          for(const [attr, val] of Object.entries(node)) {
            // Turns out, typeof null === object
            if(typeof val === "object" && val !== null) {
              // It's an object, so recursively call this method on it to get
              // the child attributes
              getFields(val).forEach( childAttr => {
                // Join the results to this attribute
                fields.push(attr + "." + childAttr);
              });
            }
            else
              fields.push(attr);
          }
          return fields;
        };

        // We only run it on the first item as a optimization. The items
        // should have the same fields after all.
        if(this.items.length !== 0)
          this.searchFields = getFields(this.items[0]);
      }
      else {
        // We were provided a list, let's use that instead
        this.searchFields = this.searchableFields;
      }
    }
  }
}
</script>