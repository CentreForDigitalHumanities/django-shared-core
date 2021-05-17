<!-- Handles the pagination bar -->
<template>
  <div class="w-100 ufl-pagination" v-if="numPages > 1">
    <ul>
      <li v-for="i in numPages" v-bind:class="{ active: i === page}" @click="switchToPage(i)">
        <span class="current" v-if="i === page">{{ i }}</span>
        <a class="page-link" v-else :href="'#page-' + i">{{ i }}</a>
      </li>
    </ul>
  </div>

</template>

<script>
export default {
  name: "Pagination",
  props: {
    numItems: {
      type: Number,
      required: true,
    },
    itemsPerPage: {
      type: Number,
      required: true,
    },
    page: {
      type: Number,
      required: true,
    },
  },
  computed: {
    numPages() {
      return Math.ceil(this.numItems / this.itemsPerPage);
    },
  },
  methods: {
    switchToPage(page) {
      this.$emit('switchToPage', page)
    }
  },
}
</script>

<style>
.ufl-pagination {
  font-size: 0.9rem;
  color: #444;
  display: block;
	overflow: hidden;
	padding: 0 5px 5px 0;
	margin: 0;
}

.ufl-pagination ul {
	list-style: none;
	padding: 0;
	margin: auto;
  display: flex;
  justify-content: center;
}

.ufl-pagination li {
	list-style: none;
	padding: 0;
	margin: 0 5px 0 0 ;
    display: inline-block;
}

.ufl-pagination li span {
	cursor: pointer;
}

.ufl-pagination a, .ufl-pagination span {
	float: left;
  height: 35px;
  width: 35px;
	font-size: 14px;
	line-height: 35px;
	font-weight: bold;
	text-align: center;
  text-decoration: none;
	border: none;
	min-width: 14px;
  color: #fff;
  padding: 0;
	background: #000000;
}

.ufl-pagination a:hover, .ufl-pagination li:not(.disabled):not(.active) span:hover {
	text-decoration: none;
    color: #000;
}

.ufl-pagination a:active {
    box-shadow: none;
}

.ufl-pagination .current {
	background: #FFCD00;
	color: #000;
	cursor: default;
}
</style>