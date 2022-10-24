<!-- Manages the control bar.
Allows setting items per page, sorting options, filters and search.
The way it interacts with it's parent is a bit complicated. Sorry, was the only
way.
-->
<template>
  <div class="uu-fancy-list-controls clearfix">
    <div class="ufl-controls-top">

      <input class="ufl-search" v-model.trim="value.search" :placeholder="$t('search_placeholder')"  />

      <label class="ufl-num-items">
        {{ $t('num_items') }}:
        <select v-model.trim="value.itemsPerPage" class="ufl-select">
          <option v-for="option in numItemsOptions" :value="option" >
            {{ option }}
          </option>
        </select>
      </label>

      <label v-if="availableSortOptions.length !== 0" class="ufl-sort-on">
        {{ $t('sort') }}:
        <select v-model.trim="value.sortOn" class="ufl-select">
          <option v-for="option in availableSortOptions" :value="option.key" >
            {{ option.label }}
          </option>
        </select>
      </label>


      <button
          v-if="availableFilters.length !== 0"
          @click="filtersVisible = !filtersVisible"
          class="ufl-filters-button btn"
          :class="{ 'btn-primary': filtersVisible }"
      >
        {{ $t('filters') }}
        <span v-if="num_selected_filters !== 0">({{ num_selected_filters }})</span>
      </button>

    </div>

    <div class="ufl-controls-bottom" v-if="filtersVisible && availableFilters.length !== 0">
      <span v-for="filter in availableFilters" :key="filter.key">
        <FilterSelect
            :label="filter.display"
            :options="filter.options"
            :value="selectedFilters[filter.key]"
            :message="filterMessage"
            @input="selectFilter(filter.key, $event)"
        >

        </FilterSelect>
      </span>
      <span>
        <div class="btn-group">
          <button
              class="btn btn-secondary ufl-filters-button"
              @click="resetFilters"
          >
            Reset
          </button>
        </div>
      </span>
    </div>
  </div>
</template>

<script>
import FilterSelect from "./FilterSelect.vue";

export default {
  name: "Controls",
  components: {
    FilterSelect
  },
  props: {
    // An array of options for items per page.
    numItemsOptions: {
      type: Array,
      required: true,
    },
    // Object of all values that can be handled using a simple v-model
    // search, itemsPerPage and sort
    value: {
      type: Object,
      required: true
    },
    // List of filter definitions
    // Should be a list of objects with the following attributes
    // key: string that FancyList.vue can couple to the field
    // display: the text to use on the filter button
    // options: a set of all options you can choose from
    availableFilters: {
      type: Array,
      default() { return []; }
    },
    // List of sort definitions
    // Should be a list of objects with the following attributes
    // key: string that FancyList.vue can couple to the field
    // label: The text that should be displayed in the dropdown
    availableSortOptions: {
      type: Array,
      default() { return []; }
    }
  },
  data() {
    return {
      // Local copy of selected filters. Should be regarded as master, with
      // the corresponding value in FancyList as follower
      selectedFilters: {},
      // Controls whether the bottom bar containing filters is showing
      filtersVisible: false,
      // Message bus to the FilterSelects
      filterMessage: undefined,
    }
  },
  computed: {
    // Returns the number of filters active
    num_selected_filters() {
      return Object.entries(this.selectedFilters).filter(
          // Object.entries returns an array of arrays
          // We use array unpacking, thus the [] inside the ()
          ([_, values]) => { return values.length !== 0 }
      ).length
    }
  },
  i18n: { // `i18n` option, setup locale info for component
    messages: {
      en: {
        search_placeholder: "Search",
        num_items: "Items per page",
        filters: "Filters",
        sort: "Sort by",
      },
      nl: {
        search_placeholder: "Zoeken",
        num_items: "Items per pagina",
        filters: "Filters",
        sort: "Sorteer op",
      }
    }
  },
  watch: {
    // If any of the v-model based items update, inform FancyList.vue
    value() {
      this.$emit('input', this.value);
    },
    // Generates entries in selectedFilters for any new filters registered
    // by FancyList. Used on startup
    availableFilters () {
      let known_filters = Object.keys(this.selectedFilters);
      this.availableFilters.forEach(filter => {
        if(!known_filters.includes(filter.key))
          this.$set(this.selectedFilters, filter.key, [])
      });
    }
  },
  methods: {
    // Sends the reset command to all FilterSelects
    // This reset will eventually bubble up to FancyList through the regular
    // filter update events
    resetFilters() {
      this.filterMessage = {
        event: "reset",
        time: new Date(), // For uniqueness
      }
    },
    // Informs FancyList.vue of any filter change
    selectFilter(key, value) {
      this.$set(this.selectedFilters, key, value);
      this.$emit('filterChange', {
        key: key,
        value: value,
      });
    },
  },
}
</script>

<style>
.uu-fancy-list-controls {
  font-size: 0.9rem;
}
.uu-fancy-list-controls .ufl-search {
  width: 200px;
  float: right;
  font-size: 0.9rem;
  border: 1px solid #ccc;
}
.uu-fancy-list-controls .ufl-select {
  font-size: 0.9rem;
  height: 28px;
  -moz-appearance:none;
  -webkit-appearance:none;
  appearance:none;
  color: #444;
  line-height: 20px;
  padding: 3px 5px;
  text-align: left;
  border: 1px solid #ccc;

  background: #fff;
  background-image:
      linear-gradient(45deg, transparent 50%, gray 50%),
      linear-gradient(135deg, gray 50%, transparent 50%),
      linear-gradient(to right, #ccc, #ccc);
  background-position:
      calc(100% - 10px) calc(1em - 3px),
      calc(100% - 6px) calc(1em - 3px),
      calc(100% - 19px) 0;
  background-size:
      4px 4px,
      4px 4px,
      1px 100%;
  background-repeat: no-repeat;
}
.uu-fancy-list-controls .ufl-num-items select {
  width: 60px;
}
.uu-fancy-list-controls .ufl-sort-on {
  padding-left: 5px;
}
.uu-fancy-list-controls .ufl-sort-on select {
  width: auto;
  padding-right: 30px;
}
.uu-fancy-list-controls .ufl-controls-bottom {
  padding-top: 10px;
}
.uu-fancy-list-controls .ufl-filters-button {
  font-size: 0.9rem;
  line-height: 28px;
  margin-left: 5px;
  padding: 0 10px;
}

@media (max-width: 767px) {
  .uu-fancy-list-controls .ufl-search  {
    width: 100%;
    margin: 10px 0;
    float: none;
  }

  .uu-fancy-list-controls .ufl-sort-on {
    padding-left: 0;
    margin-top: 10px;
    display: block;
  }

  .uu-fancy-list-controls .ufl-filters-button {
    display: block;
    width: 100%;
    margin: 10px 0 0 0;
  }

  .uu-fancy-list-controls .ufl-controls-bottom {
    padding-top: 0;
  }

}
</style>
