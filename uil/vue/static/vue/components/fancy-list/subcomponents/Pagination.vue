<!-- Handles the pagination bar -->
<template>
  <div class="w-100 ufl-pagination" v-if="numPages > 1">
    <ul>
      <li
          v-for="p in pages"
          v-bind:class="{ active: p === page}"
      >
        <span class="current" v-if="p === page">{{ p }}</span>
        <span class="sep" v-else-if="p === 'LEFT' || p === 'RIGHT'">
          ...
        </span>
        <a
            class="page-link"
            v-else
            :href="'#page-' + p"
            @click="switchToPage(p)"
        >
          {{ p }}
        </a>
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
    pages() {
      const startPage = Math.max(2, this.page - 2);
      const endPage = Math.min(this.numPages - 1, this.page + 2);
      let pages = this.range(startPage, endPage);

      /**
       * hasLeftSpill: has hidden pages to the left
       * hasRightSpill: has hidden pages to the right
       * spillOffset: number of hidden pages either to the left or to the right
       */
      const hasLeftSpill = startPage > 2;
      const hasRightSpill = (this.numPages - endPage) > 1;
      // 7 === total number of pages visible
      const spillOffset = 7 - (pages.length + 1);

      switch (true) {
        // handle: (1) < {5 6} [7] {8 9} (10)
        case (hasLeftSpill && !hasRightSpill): {
          const extraPages = this.range(startPage - spillOffset, startPage - 1);
          pages = ['LEFT', ...extraPages, ...pages];
          break;
        }

        // handle: (1) {2 3} [4] {5 6} > (10)
        case (!hasLeftSpill && hasRightSpill): {
          const extraPages = this.range(endPage + 1, endPage + spillOffset);
          pages = [...pages, ...extraPages, 'RIGHT'];
          break;
        }

        // handle: (1) < {4 5} [6] {7 8} > (10)
        case (hasLeftSpill && hasRightSpill):
        default: {
          pages = ['LEFT', ...pages, 'RIGHT'];
          break;
        }
      }

      return [1, ...pages, this.numPages];
    }
  },
  methods: {
    switchToPage(page) {
      this.$emit('switchToPage', page)
    },
    range(from, to, step = 1) {
      let i = from;
      const range = [];

      while (i <= to) {
        range.push(i);
        i += step;
      }

      return range;
    },
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

.ufl-pagination .sep {
  background: none;
  color: #000;
  cursor: default;
}
</style>