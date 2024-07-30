<script setup>
import {DSCList} from "cdh-vue-lib/components";
import {useI18n} from "vue-i18n";

// Required stuff
const props = defineProps(['config']);

const {t} = useI18n()

// Demo stuff
function statusColor(status) {
  switch (status) {
    case "C":
      return "green"

    case "R":
      return "orange"

    case "O":
      return "red"

    default:
      return ""
  }
}
</script>

<!-- Here you can define your translations. Please remember to use `t` in your template instead of `$t` -->
<i18n>
{
  "en": {
    "name": "Name",
    "refnum": "Reference Number",
    "status": "Status"
  },
  "nl": {
    "name": "Naam",
    "refnum": "Referentie Nummer",
    "status": "Status"
  }
}
</i18n>

<template>
  <!-- Required stuff -->
  <DSCList :config="config">
    <template #data="{data, isLoading}">
      <!-- Custom stuff -->
      <!-- Add your table here -->
      <div>
        <div v-if="isLoading">
          <!-- Show a 'loading' message if data is being loaded -->
          Loading...
        </div>
        <table class="table" v-else>
          <thead>
          <tr>
            <th>
              {{ t('name') }}
            </th>
            <th>
              {{ t('refnum') }}
            </th>
            <th>
              {{ t('status') }}
            </th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="datum in data">
            <td>
              {{ datum.project_name }}
            </td>
            <td>
              {{ datum.reference_number }}
            </td>
            <td :class="`text-bg-${statusColor(datum.status)}`">
              {{ datum.get_status_display }}
            </td>
          </tr>
          </tbody>
        </table>
      </div>
      <!-- end custom stuff, begin required stuff -->
    </template>
  </DSCList>
</template>
