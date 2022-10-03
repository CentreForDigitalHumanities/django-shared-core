<!-- Filter control for one filter
 Uses bootstrap Multiselect
 -->
<template>
  <select :id="id" class="ufl-select" multiple="multiple">
    <option v-for="option in options" :value="option">{{ format_option(option) }}</option>
  </select>
</template>

<script>
export default {
  name: "FilterSelect",
  props: {
    // Displayed on the button
    label: {
      type: String,
      required: true,
    },
    // All options that are choosable
    options: {
      type: Set,
      required: true,
    },
    // Controls.vue sends messages to all FilterSelects through this prop
    message: {
      type: Object,
    }
  },
  data() {
    return {
      // Random string, so we can setup a multiselect instance for this select
      // only
      'id': Math.random().toString(36).substring(7),
      // Keeps track of selected option in Vue
      'selected': [],
      // Holds the jQuery multiselect instance
      'multiselect': undefined,
    }
  },
  watch: {
    // If selected is changed by multiselect, inform parent
    selected () {
      this.$emit('input', this.selected);
    },
    // Receive and react to messages from parent
    message () {
      if (this.message) {
        switch (this.message.event) {
          // reset event means deselect everything
          case 'reset':
            // Deselect all options in multiselect
            this.multiselect.multiselect('deselect', this.selected);
            // Clear all options in Vue (not done automatically for some reason)
            this.selected = [];
            // Update multiselect, to force the name/title to change
            this.multiselect.multiselect('refresh');
            // Manually removed the color class, for some reason it isn't done
            // automatically. Even if it should be done automatically...
            $('#' + this.id).parent().find('.multiselect').removeClass('button-colored');
            break;
        }
      }
    }
  },
  methods: {
    /**
     * Format a filter option
     * Displays a boolean as yes, no, mostly
     * @param value
     */
    format_option(value) {
      if (typeof value === "boolean")
        value = value ? this.$t('yes') : this.$t('no');

      return value
    },
  },
  i18n: {
    messages: {
      en: {
        yes: "Yes",
        no: "No",
      },
      nl: {
        yes: "Ja",
        no: "Nee",
      },
    },
  },
  mounted() {
    // Alias `this` so we can use it in multiselect
    let vm = this;
    this.multiselect = $('#' + this.id).multiselect({
      buttonClass: 'btn btn-secondary ufl-filters-button ',
      includeSelectAllOption: false,
      buttonText() {
        if (vm.selected.length === 0)
          return vm.label

        return vm.label + " (" + vm.selected.length + ")"
      },
      onChange(option, checked) {
        // We need to manually update this value, as Vue will ignore any changes
        // that wasn't  made by Vue.
        if (checked)
          vm.selected.push($(option).val());
        else {
          let index = vm.selected.indexOf($(option).val());
          if(index > -1)
            vm.selected.splice(index, 1)
        }

        // This will change the buttons color when something is selected,
        if (vm.selected.length !== 0) {
          $('#' + vm.id).parent().find('.multiselect').addClass('btn-primary');
        }
        else {
          $('#' + vm.id).parent().find('.multiselect').removeClass('btn-primary');
        }
      }
    });
  },
}
</script>

<style>
.multiselect {
  margin-right: 5px;
}
.multiselect input {
  width: auto;
}
span.multiselect-native-select {
  position: relative;
}
span.multiselect-native-select select {
  border: 0 !important;
  clip: rect(0 0 0 0) !important;
  height: 1px !important;
  margin: -1px -1px -1px -3px !important;
  overflow: hidden !important;
  padding: 0 !important;
  position: absolute !important;
  width: 1px !important;
  left: 50%;
  top: 30px;
}
.multiselect.dropdown-toggle:after {
  display: none;
}
.multiselect {
  overflow: hidden;
  text-overflow: ellipsis;
}
.multiselect-container {
  position: absolute;
  list-style-type: none;
  margin: 0;
  padding: 0;
}
.multiselect-container .multiselect-reset .input-group {
  width: 93%;
}
.multiselect-container .multiselect-filter > .fa-search {
  z-index: 1;
  padding-left: 0.75rem;
}
.multiselect-container .multiselect-filter > input.multiselect-search {
  border: none;
  border-bottom: 1px solid lightgrey;
  padding-left: 2rem;
  margin-left: -1.625rem;
  border-bottom-right-radius: 0;
  border-bottom-left-radius: 0;
}
.multiselect-container .multiselect-filter > input.multiselect-search:focus {
  border-bottom-right-radius: 0.25rem;
  border-bottom-left-radius: 0.25rem;
}
.multiselect-container .multiselect-filter > .multiselect-moz-clear-filter {
  margin-left: -1.5rem;
  display: none;
}
.multiselect-container .multiselect-option.multiselect-group-option-indented-full {
  padding-left: 2.6rem;
}
.multiselect-container .multiselect-option.multiselect-group-option-indented {
  padding-left: 1.8rem;
}
.multiselect-container .multiselect-group {
  cursor: pointer;
}
.multiselect-container .multiselect-group.closed .dropdown-toggle::after {
  transform: rotate(-90deg);
}
.multiselect-container .multiselect-group .caret-container ~ .form-check {
  margin-left: 0.5rem;
}
.multiselect-container .multiselect-option,
.multiselect-container .multiselect-group,
.multiselect-container .multiselect-all {
  padding: 0.25rem 0.25rem 0.25rem 0.75rem;
}
.multiselect-container .multiselect-option.dropdown-item,
.multiselect-container .multiselect-group.dropdown-item,
.multiselect-container .multiselect-all.dropdown-item,
.multiselect-container .multiselect-option.dropdown-toggle,
.multiselect-container .multiselect-group.dropdown-toggle,
.multiselect-container .multiselect-all.dropdown-toggle {
  cursor: pointer;
}
.multiselect-container .multiselect-option .form-check-label,
.multiselect-container .multiselect-group .form-check-label,
.multiselect-container .multiselect-all .form-check-label {
  cursor: pointer;
}
.multiselect-container .multiselect-option.active:not(.multiselect-active-item-fallback),
.multiselect-container .multiselect-group.active:not(.multiselect-active-item-fallback),
.multiselect-container .multiselect-all.active:not(.multiselect-active-item-fallback),
.multiselect-container .multiselect-option:not(.multiselect-active-item-fallback):active,
.multiselect-container .multiselect-group:not(.multiselect-active-item-fallback):active,
.multiselect-container .multiselect-all:not(.multiselect-active-item-fallback):active {
  background-color: lightgrey;
  color: black;
}
.multiselect-container .multiselect-option:hover,
.multiselect-container .multiselect-group:hover,
.multiselect-container .multiselect-all:hover,
.multiselect-container .multiselect-option:focus,
.multiselect-container .multiselect-group:focus,
.multiselect-container .multiselect-all:focus {
  background-color: darkgray !important;
}
.multiselect-container .multiselect-option .form-check,
.multiselect-container .multiselect-group .form-check,
.multiselect-container .multiselect-all .form-check {
  padding: 0 5px 0 20px;
}
.multiselect-container .multiselect-option:focus,
.multiselect-container .multiselect-group:focus,
.multiselect-container .multiselect-all:focus {
  outline: none;
}
.form-inline .multiselect-container span.form-check {
  padding: 3px 20px 3px 40px;
}
.input-group.input-group-sm > .multiselect-native-select .multiselect {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  line-height: 1.5;
  padding-right: 1.75rem;
  height: calc(1.5em + 0.5rem + 2px);
}
.input-group > .multiselect-native-select {
  flex: 1 1 auto;
  width: 1%;
}
.input-group > .multiselect-native-select > div.btn-group {
  width: 100%;
}
.input-group > .multiselect-native-select:not(:first-child) .multiselect {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}
.input-group > .multiselect-native-select:not(:last-child) .multiselect {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}
</style>
