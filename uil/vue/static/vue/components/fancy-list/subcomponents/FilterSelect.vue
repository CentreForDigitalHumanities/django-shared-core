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
      buttonClass: 'btn btn-default button ufl-filters-button ',
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
          $('#' + vm.id).parent().find('.multiselect').addClass('button-colored');
        }
        else {
          $('#' + vm.id).parent().find('.multiselect').removeClass('button-colored');
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
</style>