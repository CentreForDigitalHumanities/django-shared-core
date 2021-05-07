<!-- The actual item itself

It's actually more of a shell around 4 slots, allowing custom templates to
implement things
-->
<template>
  <div class="ufl-item clearfix" :class="{ expanded: expanded }">
    <div class="ufl-bar" @click.self="toggleDetails">
      <h4>
        <slot name="title" :item="item" :context="context" />
      </h4>

      <div class="ufl-actions" v-if="$scopedSlots.actions">
        <slot name="actions" :item="item" :context="context" />
      </div>
    </div>

    <div class="ufl-undertitle">
      <slot name="undertitle" :item="item" :context="context" />
    </div>

    <div class="ufl-details" v-if="expanded">
      <slot name="details" :item="item" :context="context" />
    </div>
  </div>
</template>

<script>
export default {
  name: 'ListItem',
  props: {
    // The item to display
    item: {
      type: Object,
      required: true
    },
    // Message bus from ListContainer
    message: {
      type: Object,
      required: false,
    },
    // Any non-item specific data given to FancyList
    context: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      // Controls if the details slot is shown or not
      expanded: false,
    }
  },
  methods: {
    toggleDetails() {
      // If expanding, notify parent. This way it can close other items
      if (this.expanded === false)
        this.$emit('expanding', this.item.pk);

      this.expanded = !this.expanded;
    },
    handleExpandingChildEvent() {
      // We are also receiving our own event back, so we need to filter that one out
      if (this.message.pk !== this.item.pk)
        this.expanded = false;
    }
  },
  watch: {
    message() {
      if (this.message) {
        switch (this.message.event)
        {
          // Set if a list item expands
          case "expanding_child":
            this.handleExpandingChildEvent();
            break;
        }
      }
    }
  }

}
</script>

<style>

.uil-fancy-list .ufl-item {
    border-bottom: 2px solid #eee;
    padding: 15px 10px;
    transition: .2s;
    background: #fff;
    width: 100%;
    z-index: 2;
    position: relative;
    top: 0;
    left: 0;
}

.uil-fancy-list .ufl-bar {
    cursor: pointer;
}

.uil-fancy-list .ufl-item:after {
    font-family: 'icomoon-additional';
    content: "\E611";
    font-size: 10px;
    color: #666;
    position: absolute;
    top: 20px;
    right: 20px;
    transition: 0.2s;
}

.uil-fancy-list .ufl-item.expanded {
    background: #f7f7f7;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.4);
    width: calc(100% + 10px);
    left: -5px;
    top: -5px;
    padding: 15px;
    margin-bottom: -10px;
    border-color: transparent;
    z-index: 3;
}

.uil-fancy-list .ufl-item.expanded:after {
    content: "\E612";
    right: 25px;
}

.uil-fancy-list .ufl-item .ufl-actions {
    display: inline-block;
    color: #666;
    font-weight: 400;
    font-size: 1.4rem;
    padding-left: 5px;
    user-select: none;
}

.uil-fancy-list .ufl-item .ufl-actions [class^="icon-"],
.uil-fancy-list .ufl-item .ufl-actions [class*=" icon-"] {
    font-size: 1rem;

}

.uil-fancy-list .ufl-item .ufl-actions a {
    text-decoration: none;
}

.uil-fancy-list .ufl-item h4 {
    display: inline-block;
    margin-bottom: 0.3rem;
    /*
    This is intentionally darker than all other text
    Due to the low-weight of this text, it appears lighter than it is.
    Making it pure black actually makes it appear more visually consistent with
    other text
     */
    color: #000;
}

.uil-fancy-list .ufl-item .ufl-undertitle {
    font-weight: 400;
    font-size: 0.9rem;
    color: #555;
}

.uil-fancy-list .ufl-item .ufl-undertitle .ufl-undertitle-line {
    display: inline-block;
}

.uil-fancy-list .ufl-item .ufl-undertitle .ufl-undertitle-line:not(:first-of-type) {
    margin-left: 4px;
}

.uil-fancy-list .ufl-item .ufl-details {
    color: #444;
    padding-top: 10px;
    font-size: 0.9rem;
    cursor: auto;
}

.uil-fancy-list .ufl-item .ufl-details tr,
.uil-fancy-list .ufl-item .ufl-details tr {
    background: none;
}

@media (min-width: 767px) {
    .uil-fancy-list .ufl-item .ufl-undertitle .ufl-undertitle-line:not(:first-of-type):before {
        content: '';
        width: 1px;
        height: 16px;
        background: #aaa;
        position: relative;
        left: -2px;
        bottom: -4px;
        display: inline-block;
    }

    .uil-fancy-list .ufl-item .ufl-actions:before {
        content: '';
        width: 1px;
        height: 22px;
        background: #aaa;
        position: relative;
        left: -2px;
        bottom: -4px;
        display: inline-block;
    }
}

@media (max-width: 767px) {
    .uil-fancy-list .ufl-item .ufl-actions {
        display: flex;
        flex-direction: row;
        justify-content: space-around;
        width: 100%;
    }
    .uil-fancy-list .ufl-item .ufl-undertitle .ufl-undertitle-line {
        display: block;
        margin-left: 4px;
    }
    .uil-fancy-list .ufl-item .ufl-undertitle .ufl-undertitle-line:not(:first-of-type):before {
        width: 0;
    }
}

</style>