var CustomList = function(vue, vueI18n) {
  "use strict";
  let getRandomValues;
  const rnds8 = new Uint8Array(16);
  function rng() {
    if (!getRandomValues) {
      getRandomValues = typeof crypto !== "undefined" && crypto.getRandomValues && crypto.getRandomValues.bind(crypto);
      if (!getRandomValues) {
        throw new Error("crypto.getRandomValues() not supported. See https://github.com/uuidjs/uuid#getrandomvalues-not-supported");
      }
    }
    return getRandomValues(rnds8);
  }
  const byteToHex = [];
  for (let i = 0; i < 256; ++i) {
    byteToHex.push((i + 256).toString(16).slice(1));
  }
  function unsafeStringify(arr, offset = 0) {
    return (byteToHex[arr[offset + 0]] + byteToHex[arr[offset + 1]] + byteToHex[arr[offset + 2]] + byteToHex[arr[offset + 3]] + "-" + byteToHex[arr[offset + 4]] + byteToHex[arr[offset + 5]] + "-" + byteToHex[arr[offset + 6]] + byteToHex[arr[offset + 7]] + "-" + byteToHex[arr[offset + 8]] + byteToHex[arr[offset + 9]] + "-" + byteToHex[arr[offset + 10]] + byteToHex[arr[offset + 11]] + byteToHex[arr[offset + 12]] + byteToHex[arr[offset + 13]] + byteToHex[arr[offset + 14]] + byteToHex[arr[offset + 15]]).toLowerCase();
  }
  const randomUUID = typeof crypto !== "undefined" && crypto.randomUUID && crypto.randomUUID.bind(crypto);
  const native = {
    randomUUID
  };
  function v4(options, buf, offset) {
    if (native.randomUUID && !buf && !options) {
      return native.randomUUID();
    }
    options = options || {};
    const rnds = options.random || (options.rng || rng)();
    rnds[6] = rnds[6] & 15 | 64;
    rnds[8] = rnds[8] & 63 | 128;
    if (buf) {
      offset = offset || 0;
      for (let i = 0; i < 16; ++i) {
        buf[offset + i] = rnds[i];
      }
      return buf;
    }
    return unsafeStringify(rnds);
  }
  /*!
  * Copyright 2022, 2023 Utrecht University
  *
  * Licensed under the EUPL, Version 1.2 only
  * You may not use this work except in compliance with the
  Licence.
  * A copy of the Licence is provided in the 'LICENCE' file in this project.
  * You may also obtain a copy of the Licence at:
  *
  * https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
  *
  * Unless required by applicable law or agreed to in
  writing, software distributed under the Licence is
  distributed on an "AS IS" basis,
  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
  express or implied.
  * See the Licence for the specific language governing
  permissions and limitations under the Licence.
  */
  function t(e) {
    return e.target.value;
  }
  /*!
  * Copyright 2022, 2023 Utrecht University
  *
  * Licensed under the EUPL, Version 1.2 only
  * You may not use this work except in compliance with the
  Licence.
  * A copy of the Licence is provided in the 'LICENCE' file in this project.
  * You may also obtain a copy of the Licence at:
  *
  * https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
  *
  * Unless required by applicable law or agreed to in
  writing, software distributed under the Licence is
  distributed on an "AS IS" basis,
  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
  express or implied.
  * See the Licence for the specific language governing
  permissions and limitations under the Licence.
  */
  const re = ["href", "target"], ie = { class: "btn-text" }, ue = ["type", "name", "disabled"], de = { class: "btn-text" }, Y = /* @__PURE__ */ vue.defineComponent({
    __name: "BSButton",
    props: {
      id: { default: null },
      href: { default: void 0 },
      name: { default: void 0 },
      variant: { default: "dark" },
      size: { default: "normal" },
      outlined: { type: Boolean, default: false },
      active: { type: Boolean, default: false },
      disabled: { type: Boolean, default: false },
      loading: { type: Boolean, default: false },
      input: { default: "button" },
      newTab: { type: Boolean, default: false },
      cssClasses: { default: "" }
    },
    setup(i) {
      const t2 = i, o = vue.computed(() => {
        let n = "btn ";
        return t2.size === "large" ? n += "btn-lg " : t2.size === "small" && (n += "btn-sm "), t2.outlined ? n += "btn-outline-" : n += "btn-", n += `${t2.variant} `, t2.loading && (n += "btn-loading "), t2.active && (n += "active "), n;
      });
      return (n, e) => n.href ? (vue.openBlock(), vue.createElementBlock("a", {
        key: 0,
        href: n.href,
        class: vue.normalizeClass(o.value),
        target: n.newTab ? "_blank" : "_self"
      }, [
        vue.createElementVNode("span", ie, [
          vue.renderSlot(n.$slots, "default")
        ])
      ], 10, re)) : (vue.openBlock(), vue.createElementBlock("button", {
        key: 1,
        type: n.input,
        class: vue.normalizeClass(o.value),
        name: n.name,
        disabled: n.disabled
      }, [
        vue.createElementVNode("span", de, [
          vue.renderSlot(n.$slots, "default")
        ])
      ], 10, ue));
    }
  });
  const Ve = ["id", "value", "checked", "onClick"], De = ["for"], Ue = /* @__PURE__ */ vue.defineComponent({
    __name: "BSMultiSelect",
    props: {
      options: {},
      modelValue: {},
      containerClasses: { default: "" },
      uniqueId: { default: v4().toString() }
    },
    emits: ["update:modelValue", "update:model-value"],
    setup(i, { emit: t2 }) {
      const o = i;
      function n(e) {
        const l = o.modelValue.includes(e);
        let a = [...o.modelValue];
        if (!l)
          a.push(e);
        else {
          const u = a.indexOf(e);
          u > -1 && a.splice(u, 1);
        }
        t2("update:modelValue", a);
      }
      return (e, l) => (vue.openBlock(), vue.createElementBlock("div", null, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(e.options, ([a, u]) => (vue.openBlock(), vue.createElementBlock("div", {
          key: a,
          class: vue.normalizeClass(["form-check", e.containerClasses])
        }, [
          vue.createElementVNode("input", {
            id: "id_" + a + "_" + e.uniqueId,
            type: "checkbox",
            class: "form-check-input",
            value: a,
            checked: o.modelValue.includes(a),
            onClick: (_) => n(a)
          }, null, 8, Ve),
          vue.createElementVNode("label", {
            class: "form-check-label",
            for: +"_" + e.uniqueId
          }, vue.toDisplayString(u), 9, De)
        ], 2))), 128))
      ]));
    }
  }), Le = {
    class: "pagination justify-content-center",
    role: "navigation",
    "aria-label": "pagination"
  }, Oe = ["onClick"], Ie = {
    key: 1,
    class: "page-link"
  }, q = /* @__PURE__ */ vue.defineComponent({
    __name: "BSPagination",
    props: {
      maxPages: {},
      currentpage: {},
      showButtons: { type: Boolean, default: true },
      numOptions: { default: 2 }
    },
    emits: ["change-page"],
    setup(i, { emit: t2 }) {
      const o = i;
      function n(u, _, y) {
        return Math.min(Math.max(u, _), y);
      }
      const e = vue.computed(() => {
        const u = o.numOptions, _ = o.currentpage - u, y = o.currentpage + u + 1, P = [], I = [];
        let U;
        for (let $ = 1; $ <= o.maxPages; $++)
          ($ === 1 || $ === o.maxPages || $ >= _ && $ < y) && P.push($);
        for (const $ of P)
          U && ($ - U === 2 ? I.push(U + 1) : $ - U !== 1 && I.push(-42)), I.push($), U = $;
        return I;
      });
      function l(u) {
        u = n(u, 1, o.maxPages), t2("change-page", u);
      }
      const { t: a } = vueI18n.useI18n();
      return (u, _) => (vue.openBlock(), vue.createElementBlock("ul", Le, [
        vue.createElementVNode("li", {
          class: vue.normalizeClass(["page-item page-button", u.currentpage === 1 ? "disabled" : ""])
        }, [
          u.showButtons ? (vue.openBlock(), vue.createElementBlock("a", {
            key: 0,
            class: "page-link",
            onClick: _[0] || (_[0] = (y) => l(u.currentpage - 1))
          }, vue.toDisplayString(vue.unref(a)("previous")), 1)) : vue.createCommentVNode("", true)
        ], 2),
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(e.value, (y) => (vue.openBlock(), vue.createElementBlock("li", {
          key: y,
          class: vue.normalizeClass([
            "page-item",
            (y === -42 ? "disabled page-ellipsis " : "") + (y === u.currentpage ? "active" : "")
          ])
        }, [
          y !== -42 ? (vue.openBlock(), vue.createElementBlock("a", {
            key: 0,
            class: "page-link",
            onClick: (P) => l(y)
          }, vue.toDisplayString(y), 9, Oe)) : (vue.openBlock(), vue.createElementBlock("span", Ie, "…"))
        ], 2))), 128)),
        vue.createElementVNode("li", {
          class: vue.normalizeClass(["page-item page-button", u.currentpage >= u.maxPages ? "disabled" : ""])
        }, [
          u.showButtons ? (vue.openBlock(), vue.createElementBlock("a", {
            key: 0,
            class: "page-link",
            onClick: _[1] || (_[1] = (y) => l(u.currentpage + 1))
          }, vue.toDisplayString(vue.unref(a)("next")), 1)) : vue.createCommentVNode("", true)
        ], 2)
      ]));
    }
  });
  function Q(i) {
    const t2 = i;
    t2.__i18n = t2.__i18n || [], t2.__i18n.push({
      locale: "",
      resource: {
        en: {
          next: (o) => {
            const { normalize: n } = o;
            return n(["Next"]);
          },
          previous: (o) => {
            const { normalize: n } = o;
            return n(["Previous"]);
          }
        },
        nl: {
          next: (o) => {
            const { normalize: n } = o;
            return n(["Volgende"]);
          },
          previous: (o) => {
            const { normalize: n } = o;
            return n(["Vorige"]);
          }
        }
      }
    });
  }
  typeof Q == "function" && Q(q);
  const Pe = ["id", "value", "checked", "onClick"], Ee = ["for"], Ne = /* @__PURE__ */ vue.defineComponent({
    __name: "BSRadioSelect",
    props: {
      options: {},
      modelValue: {},
      containerClasses: { default: "" }
    },
    emits: ["update:modelValue", "update:model-value"],
    setup(i, { emit: t2 }) {
      return (o, n) => (vue.openBlock(), vue.createElementBlock("div", null, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(o.options, ([e, l]) => (vue.openBlock(), vue.createElementBlock("div", {
          key: e,
          class: vue.normalizeClass(["form-check", o.containerClasses])
        }, [
          vue.createElementVNode("input", {
            id: "id_" + e,
            type: "radio",
            class: "form-check-input",
            value: e,
            checked: o.modelValue == e,
            onClick: (a) => t2("update:model-value", e)
          }, null, 8, Pe),
          vue.createElementVNode("label", {
            class: "form-check-label",
            for: "id_" + e
          }, vue.toDisplayString(l), 9, Ee)
        ], 2))), 128))
      ]));
    }
  }), Me = { class: "uu-sidebar" }, Te = ["data-bs-target"], qe = ["id"], Re = { class: "uu-sidebar-content" }, je = /* @__PURE__ */ vue.defineComponent({
    __name: "BSSidebar",
    props: {
      id: { default: null },
      placement: { default: "left" },
      mobilePlacement: { default: "top" },
      stickySidebar: { type: Boolean, default: false },
      mobileStickySidebar: { type: Boolean, default: false }
    },
    setup(i) {
      const t2 = i, o = vue.computed(() => t2.id !== null ? t2.id : "id_" + v4().toString().replace(/-/g, "")), n = vue.computed(() => {
        let e = "";
        return t2.placement === "right" && (e += "uu-sidebar-right "), t2.mobilePlacement === "bottom" && (e += "uu-sidebar-mobile-bottom "), t2.stickySidebar && (e += "uu-sidebar-sticky "), t2.mobileStickySidebar && (e += "uu-sidebar-mobile-sticky "), e;
      });
      return (e, l) => (vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["uu-sidebar-container", n.value])
      }, [
        vue.createElementVNode("aside", Me, [
          vue.createElementVNode("button", {
            class: "uu-sidebar-toggle",
            type: "button",
            "data-bs-toggle": "collapse",
            "data-bs-target": "#" + o.value,
            "aria-expanded": "false"
          }, [
            vue.renderSlot(e.$slots, "sidebar-button")
          ], 8, Te),
          vue.createElementVNode("div", {
            id: o.value,
            class: "uu-sidebar-collapse collapse"
          }, [
            vue.renderSlot(e.$slots, "sidebar")
          ], 8, qe)
        ]),
        vue.createElementVNode("div", Re, [
          vue.renderSlot(e.$slots, "default")
        ])
      ], 2));
    }
  }), Fe = { class: "uu-list-filter" }, Ze = { class: "uu-list-filter-label" }, Ge = {
    key: 2,
    class: "uu-list-filter-field"
  }, Qe = ["value"], We = /* @__PURE__ */ vue.defineComponent({
    __name: "Filter",
    props: {
      filter: {},
      value: {}
    },
    emits: ["update:value"],
    setup(i, { emit: t$1 }) {
      return (o, n) => (vue.openBlock(), vue.createElementBlock("div", Fe, [
        vue.createElementVNode("div", Ze, vue.toDisplayString(o.filter.label), 1),
        o.filter.type === "checkbox" ? (vue.openBlock(), vue.createBlock(vue.unref(Ue), {
          key: 0,
          options: o.filter.options ?? [],
          "model-value": o.value ?? [],
          "onUpdate:modelValue": n[0] || (n[0] = (e) => t$1("update:value", e))
        }, null, 8, ["options", "model-value"])) : vue.createCommentVNode("", true),
        o.filter.type === "radio" ? (vue.openBlock(), vue.createBlock(vue.unref(Ne), {
          key: 1,
          options: o.filter.options ?? [],
          "model-value": o.value ?? "",
          "onUpdate:modelValue": n[1] || (n[1] = (e) => t$1("update:value", e))
        }, null, 8, ["options", "model-value"])) : vue.createCommentVNode("", true),
        o.filter.type === "date" ? (vue.openBlock(), vue.createElementBlock("div", Ge, [
          vue.createElementVNode("input", {
            type: "date",
            value: o.value,
            class: "form-control",
            onInput: n[2] || (n[2] = (e) => t$1("update:value", vue.unref(t)(e)))
          }, null, 40, Qe)
        ])) : vue.createCommentVNode("", true)
      ]));
    }
  }), Ae = { key: 0 }, x = /* @__PURE__ */ vue.defineComponent({
    __name: "FilterBar",
    props: {
      filters: {},
      filterValues: {}
    },
    emits: ["update:filter-values"],
    setup(i, { emit: t2 }) {
      const o = i;
      function n(e, l) {
        let a = { ...o.filterValues };
        a[e] = l, t2("update:filter-values", a);
      }
      return (e, l) => e.filters ? (vue.openBlock(), vue.createElementBlock("div", Ae, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(e.filters, (a) => (vue.openBlock(), vue.createBlock(We, {
          key: a.field,
          filter: a,
          value: e.filterValues[a.field] ?? void 0,
          "onUpdate:value": (u) => n(a.field, u)
        }, null, 8, ["filter", "value", "onUpdate:value"]))), 128))
      ])) : vue.createCommentVNode("", true);
    }
  }), He = { class: "search" }, Je = ["value", "placeholder"], R = /* @__PURE__ */ vue.defineComponent({
    __name: "SearchControl",
    props: {
      modelValue: {}
    },
    emits: ["update:modelValue", "update:model-value"],
    setup(i, { emit: t$1 }) {
      function o(a, u = 500) {
        let _;
        return (...y) => {
          clearTimeout(_), _ = setTimeout(() => {
            a.apply(this, y);
          }, u);
        };
      }
      function n(a) {
        t$1("update:modelValue", a);
      }
      const e = o((a) => n(a)), { t: l } = vueI18n.useI18n();
      return (a, u) => (vue.openBlock(), vue.createElementBlock("div", He, [
        vue.createElementVNode("input", {
          id: "search",
          class: "form-control",
          value: a.modelValue,
          placeholder: vue.unref(l)("placeholder"),
          onInput: u[0] || (u[0] = (_) => vue.unref(e)(vue.unref(t)(_)))
        }, null, 40, Je)
      ]));
    }
  });
  function W(i) {
    const t2 = i;
    t2.__i18n = t2.__i18n || [], t2.__i18n.push({
      locale: "",
      resource: {
        en: {
          placeholder: (o) => {
            const { normalize: n } = o;
            return n(["Search"]);
          }
        },
        nl: {
          placeholder: (o) => {
            const { normalize: n } = o;
            return n(["Zoeken"]);
          }
        }
      }
    });
  }
  typeof W == "function" && W(R);
  const Ke = ["value"], Xe = ["value"], ee = /* @__PURE__ */ vue.defineComponent({
    __name: "PageSizeControl",
    props: {
      pageSize: {},
      pageSizeOptions: {}
    },
    emits: ["update:pageSize", "update:page-size"],
    setup(i, { emit: t$1 }) {
      const o = i;
      function n(e) {
        if (typeof e == "string")
          try {
            e = Number(e);
          } catch {
            e = o.pageSizeOptions[0] ?? 10;
          }
        t$1("update:pageSize", e);
      }
      return (e, l) => (vue.openBlock(), vue.createElementBlock("select", {
        value: e.pageSize,
        class: "form-select",
        onChange: l[0] || (l[0] = (a) => n(vue.unref(t)(a)))
      }, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(e.pageSizeOptions, (a) => (vue.openBlock(), vue.createElementBlock("option", {
          key: a,
          value: a
        }, vue.toDisplayString(a), 9, Xe))), 128))
      ], 40, Ke));
    }
  }), Ye = ["value"], xe = ["value"], te = /* @__PURE__ */ vue.defineComponent({
    __name: "SortControl",
    props: {
      currentSort: {},
      sortOptions: {}
    },
    emits: ["update:current-sort", "update:currentSort"],
    setup(i, { emit: t$1 }) {
      return (o, n) => (vue.openBlock(), vue.createElementBlock("select", {
        value: o.currentSort,
        class: "form-select",
        onChange: n[0] || (n[0] = (e) => o.$emit("update:current-sort", vue.unref(t)(e).trim()))
      }, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(o.sortOptions, ({ field: e, label: l }) => (vue.openBlock(), vue.createElementBlock("option", {
          key: e,
          value: e
        }, vue.toDisplayString(l), 9, xe))), 128))
      ], 40, Ye));
    }
  }), et = { key: 0 }, j = /* @__PURE__ */ vue.defineComponent({
    __name: "SearchResultNum",
    props: {
      searchQuery: {},
      pageNum: {},
      totalNum: {}
    },
    setup(i) {
      const { t: t2 } = vueI18n.useI18n();
      return (o, n) => (vue.openBlock(), vue.createElementBlock("div", null, [
        o.searchQuery ? (vue.openBlock(), vue.createElementBlock("span", et, vue.toDisplayString(vue.unref(t2)("search", { query: o.searchQuery })), 1)) : vue.createCommentVNode("", true),
        vue.createTextVNode(" " + vue.toDisplayString(vue.unref(t2)("showing", {
          pageNum: o.pageNum,
          totalNum: Intl.NumberFormat().format(o.totalNum)
        })), 1)
      ]));
    }
  });
  function A(i) {
    const t2 = i;
    t2.__i18n = t2.__i18n || [], t2.__i18n.push({
      locale: "",
      resource: {
        en: {
          search: (o) => {
            const { normalize: n, interpolate: e, named: l } = o;
            return n(["Search result: ", e(l("query")), ","]);
          },
          showing: (o) => {
            const { normalize: n, interpolate: e, named: l } = o;
            return n(["showing ", e(l("pageNum")), " of ", e(l("totalNum")), " results"]);
          }
        },
        nl: {
          search: (o) => {
            const { normalize: n, interpolate: e, named: l } = o;
            return n(["Zoekresultaat: ", e(l("query")), ","]);
          },
          showing: (o) => {
            const { normalize: n, interpolate: e, named: l } = o;
            return n([e(l("pageNum")), " van ", e(l("totalNum")), " getoond"]);
          }
        }
      }
    });
  }
  typeof A == "function" && A(j);
  const tt = { class: "uu-container" }, nt = { class: "uu-list" }, ot = { class: "uu-list-controls" }, at = {
    key: 1,
    class: "uu-list-order-control"
  }, st = { class: "uu-list-page-size-control" }, lt = {
    key: 0,
    class: "uu-list-filters"
  }, rt = { class: "uu-list-content" }, it = /* @__PURE__ */ vue.defineComponent({
    __name: "Default",
    props: {
      data: {},
      isLoading: { type: Boolean },
      totalData: {},
      currentPage: {},
      searchEnabled: { type: Boolean },
      search: {},
      sortEnabled: { type: Boolean },
      currentSort: {},
      sortOptions: {},
      pageSize: {},
      pageSizeOptions: {},
      filtersEnabled: { type: Boolean },
      filters: {},
      filterValues: {}
    },
    emits: ["update:current-page", "update:search", "update:current-sort", "update:page-size", "update:filter-values"],
    setup(i, { emit: t2 }) {
      const o = i, n = vue.computed(() => Math.ceil(o.totalData / o.pageSize));
      return (e, l) => {
        var a;
        return vue.openBlock(), vue.createElementBlock("div", tt, [
          vue.createElementVNode("div", nt, [
            vue.createElementVNode("div", ot, [
              e.searchEnabled ? (vue.openBlock(), vue.createBlock(R, {
                key: 0,
                "model-value": e.search,
                class: "uu-list-search-control",
                "onUpdate:modelValue": l[0] || (l[0] = (u) => e.$emit("update:search", u))
              }, null, 8, ["model-value"])) : vue.createCommentVNode("", true),
              vue.createVNode(j, {
                "search-query": e.search,
                "page-num": ((a = e.data) == null ? void 0 : a.length) ?? 0,
                "total-num": e.totalData,
                class: "uu-list-search-text-control"
              }, null, 8, ["search-query", "page-num", "total-num"]),
              e.sortEnabled ? (vue.openBlock(), vue.createElementBlock("div", at, [
                vue.createVNode(te, {
                  "current-sort": e.currentSort,
                  "sort-options": e.sortOptions,
                  "onUpdate:currentSort": l[1] || (l[1] = (u) => t2("update:current-sort", u))
                }, null, 8, ["current-sort", "sort-options"])
              ])) : vue.createCommentVNode("", true),
              vue.createElementVNode("div", st, [
                vue.createVNode(ee, {
                  "page-size-options": e.pageSizeOptions,
                  "page-size": e.pageSize,
                  "onUpdate:pageSize": l[2] || (l[2] = (u) => t2("update:page-size", u))
                }, null, 8, ["page-size-options", "page-size"])
              ])
            ]),
            e.filtersEnabled ? (vue.openBlock(), vue.createElementBlock("div", lt, [
              vue.renderSlot(e.$slots, "filters-top", {
                data: e.data,
                isLoading: e.isLoading
              }),
              vue.createVNode(x, {
                filters: e.filters,
                "filter-values": e.filterValues,
                "onUpdate:filterValues": l[3] || (l[3] = (u) => e.$emit("update:filter-values", u))
              }, null, 8, ["filters", "filter-values"]),
              vue.renderSlot(e.$slots, "filters-bottom", {
                data: e.data,
                isLoading: e.isLoading
              })
            ])) : vue.createCommentVNode("", true),
            vue.createElementVNode("div", rt, [
              vue.renderSlot(e.$slots, "data", {
                data: e.data,
                isLoading: e.isLoading
              }),
              vue.createElementVNode("div", null, [
                e.data ? (vue.openBlock(), vue.createBlock(vue.unref(q), {
                  key: 0,
                  "max-pages": n.value,
                  currentpage: e.currentPage,
                  onChangePage: l[4] || (l[4] = (u) => e.$emit("update:current-page", u))
                }, null, 8, ["max-pages", "currentpage"])) : vue.createCommentVNode("", true)
              ])
            ])
          ])
        ]);
      };
    }
  }), ut = { class: "w-100 d-flex align-items-center gap-3 uu-list-controls" }, dt = {
    key: 0,
    class: "ms-auto"
  }, ne = /* @__PURE__ */ vue.defineComponent({
    __name: "Sidebar",
    props: {
      data: {},
      isLoading: { type: Boolean },
      totalData: {},
      currentPage: {},
      searchEnabled: { type: Boolean },
      search: {},
      sortEnabled: { type: Boolean },
      currentSort: {},
      sortOptions: {},
      pageSize: {},
      pageSizeOptions: {},
      filtersEnabled: { type: Boolean },
      filters: {},
      filterValues: {}
    },
    emits: ["update:current-page", "update:search", "update:current-sort", "update:page-size", "update:filter-values"],
    setup(i, { emit: t2 }) {
      const o = i, n = vue.computed(() => Math.ceil(o.totalData / o.pageSize));
      return (e, l) => (vue.openBlock(), vue.createBlock(vue.unref(je), { class: "uu-list-sidebar" }, {
        sidebar: vue.withCtx(() => [
          e.searchEnabled ? (vue.openBlock(), vue.createBlock(R, {
            key: 0,
            "model-value": e.search,
            "onUpdate:modelValue": l[0] || (l[0] = (a) => e.$emit("update:search", a))
          }, null, 8, ["model-value"])) : vue.createCommentVNode("", true),
          vue.renderSlot(e.$slots, "filters-top", {
            data: e.data,
            isLoading: e.isLoading
          }),
          e.filters ? (vue.openBlock(), vue.createBlock(x, {
            key: 1,
            filters: e.filters,
            "filter-values": e.filterValues,
            "onUpdate:filterValues": l[1] || (l[1] = (a) => e.$emit("update:filter-values", a))
          }, null, 8, ["filters", "filter-values"])) : vue.createCommentVNode("", true),
          vue.renderSlot(e.$slots, "filters-bottom", {
            data: e.data,
            isLoading: e.isLoading
          })
        ]),
        default: vue.withCtx(() => {
          var a;
          return [
            vue.createElementVNode("div", null, [
              vue.createElementVNode("div", ut, [
                vue.createVNode(j, {
                  "search-query": e.search,
                  "page-num": ((a = e.data) == null ? void 0 : a.length) ?? 0,
                  "total-num": e.totalData
                }, null, 8, ["search-query", "page-num", "total-num"]),
                e.sortEnabled ? (vue.openBlock(), vue.createElementBlock("div", dt, [
                  vue.createVNode(te, {
                    "current-sort": e.currentSort,
                    "sort-options": e.sortOptions,
                    "onUpdate:currentSort": l[2] || (l[2] = (u) => t2("update:current-sort", u))
                  }, null, 8, ["current-sort", "sort-options"])
                ])) : vue.createCommentVNode("", true),
                vue.createElementVNode("div", null, [
                  vue.createVNode(ee, {
                    "page-size-options": e.pageSizeOptions,
                    "page-size": e.pageSize,
                    "onUpdate:pageSize": l[3] || (l[3] = (u) => t2("update:page-size", u))
                  }, null, 8, ["page-size-options", "page-size"])
                ])
              ]),
              vue.renderSlot(e.$slots, "data", {
                data: e.data,
                isLoading: e.isLoading
              }),
              vue.createElementVNode("div", null, [
                e.data ? (vue.openBlock(), vue.createBlock(vue.unref(q), {
                  key: 0,
                  "max-pages": n.value,
                  currentpage: e.currentPage,
                  onChangePage: l[4] || (l[4] = (u) => e.$emit("update:current-page", u))
                }, null, 8, ["max-pages", "currentpage"])) : vue.createCommentVNode("", true)
              ])
            ])
          ];
        }),
        _: 3
      }));
    }
  });
  function H(i) {
    const t2 = i;
    t2.__i18n = t2.__i18n || [], t2.__i18n.push({
      locale: "",
      resource: {
        en: {
          loading: (o) => {
            const { normalize: n } = o;
            return n(["Loading...."]);
          },
          no_data: (o) => {
            const { normalize: n } = o;
            return n(["No items to display"]);
          }
        },
        nl: {
          loading: (o) => {
            const { normalize: n } = o;
            return n(["Gegevens worden laden..."]);
          },
          no_data: (o) => {
            const { normalize: n } = o;
            return n(["Geen gegevens om te tonen"]);
          }
        }
      }
    });
  }
  typeof H == "function" && H(ne);
  const pt = /* @__PURE__ */ vue.defineComponent({
    __name: "DebugVisualizer",
    props: {
      data: { default: void 0 },
      isLoading: { type: Boolean, default: false }
    },
    setup(i) {
      return (t2, o) => (vue.openBlock(), vue.createElementBlock("pre", null, vue.toDisplayString(t2.data), 1));
    }
  }), ct = /* @__PURE__ */ vue.defineComponent({
    __name: "UUList",
    props: {
      container: { default: "default" },
      data: {},
      isLoading: { type: Boolean, default: false },
      totalData: {},
      currentPage: {},
      searchEnabled: { type: Boolean, default: false },
      search: { default: "" },
      sortEnabled: { type: Boolean, default: false },
      currentSort: { default: "" },
      sortOptions: { default: () => [] },
      pageSize: { default: 10 },
      pageSizeOptions: { default: () => [10, 25, 50] },
      filtersEnabled: { type: Boolean, default: false },
      filters: {},
      filterValues: {}
    },
    emits: ["update:current-page", "update:search", "update:current-sort", "update:page-size", "update:filter-values"],
    setup(i, { emit: t2 }) {
      const o = i, n = vue.computed(() => {
        switch (o.container) {
          case "sidebar":
            return ne;
          default:
            return it;
        }
      });
      return (e, l) => (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(n.value), {
        "is-loading": e.isLoading,
        data: e.data,
        "total-data": e.totalData,
        "search-enabled": e.searchEnabled,
        search: e.search,
        "sort-enabled": e.sortEnabled,
        "current-sort": e.currentSort,
        "current-page": e.currentPage,
        "page-size-options": e.pageSizeOptions,
        "sort-options": e.sortOptions,
        "page-size": e.pageSize,
        "filters-enabled": e.filtersEnabled,
        filters: e.filters,
        "filter-values": e.filterValues,
        "onUpdate:search": l[0] || (l[0] = (a) => t2("update:search", a)),
        "onUpdate:currentSort": l[1] || (l[1] = (a) => t2("update:current-sort", a)),
        "onUpdate:pageSize": l[2] || (l[2] = (a) => t2("update:page-size", a)),
        "onUpdate:currentPage": l[3] || (l[3] = (a) => t2("update:current-page", a)),
        "onUpdate:filterValues": l[4] || (l[4] = (a) => t2("update:filter-values", a))
      }, {
        data: vue.withCtx(({ data: a, isLoading: u }) => [
          vue.renderSlot(e.$slots, "data", {
            data: a,
            isLoading: u
          }, () => [
            vue.createVNode(pt, {
              data: a,
              "is-loading": u
            }, null, 8, ["data", "is-loading"])
          ])
        ]),
        "filters-top": vue.withCtx(({ data: a, isLoading: u }) => [
          vue.renderSlot(e.$slots, "filters-top", {
            data: a,
            isLoading: u
          })
        ]),
        "filters-bottom": vue.withCtx(({ data: a, isLoading: u }) => [
          vue.renderSlot(e.$slots, "filters-bottom", {
            data: a,
            isLoading: u
          })
        ]),
        _: 3
      }, 40, ["is-loading", "data", "total-data", "search-enabled", "search", "sort-enabled", "current-sort", "current-page", "page-size-options", "sort-options", "page-size", "filters-enabled", "filters", "filter-values"]));
    }
  }), mt = /* @__PURE__ */ vue.defineComponent({
    __name: "DDVString",
    props: {
      item: {},
      column: {}
    },
    setup(i) {
      return (t2, o) => (vue.openBlock(), vue.createElementBlock("span", {
        class: vue.normalizeClass(t2.column.classes)
      }, vue.toDisplayString(t2.item[t2.column.field]), 3));
    }
  }), ft = /* @__PURE__ */ vue.defineComponent({
    __name: "DDVDate",
    props: {
      item: {},
      column: {}
    },
    setup(i) {
      const t2 = i, o = vue.computed(() => {
        let n = null;
        try {
          n = new Date(t2.item[t2.column.field]);
        } catch (a) {
          return console.error(a), "";
        }
        let e;
        if (t2.column.language !== void 0 && t2.column.language !== null && (e = t2.column.language), typeof t2.column.format == "string") {
          let a = null;
          switch (t2.column.format) {
            case "date":
              a = {
                dateStyle: "medium"
              };
              break;
            case "time":
              a = {
                timeStyle: "short"
              };
              break;
            case "datetime":
              a = {
                dateStyle: "medium",
                timeStyle: "short"
              };
              break;
          }
          return new Intl.DateTimeFormat(e, a).format(n);
        }
        return typeof t2.column.format == "object" && t2.column.format !== null ? new Intl.DateTimeFormat(
          e,
          t2.column.format
        ).format(n) : new Intl.DateTimeFormat(e).format(n);
      });
      return (n, e) => (vue.openBlock(), vue.createElementBlock("span", {
        class: vue.normalizeClass(n.column.classes)
      }, vue.toDisplayString(o.value), 3));
    }
  }), gt = { key: 0 }, ht = /* @__PURE__ */ vue.defineComponent({
    __name: "DDVButton",
    props: {
      item: {},
      column: {}
    },
    setup(i) {
      return (t2, o) => t2.item[t2.column.field] ? (vue.openBlock(), vue.createElementBlock("span", gt, [
        vue.createVNode(vue.unref(Y), {
          href: t2.item[t2.column.field].link,
          "css-classes": t2.item[t2.column.field].classes,
          "new-tab": t2.item[t2.column.field].new_tab,
          size: t2.column.size,
          variant: t2.column.variant
        }, {
          default: vue.withCtx(() => [
            vue.createTextVNode(vue.toDisplayString(t2.item[t2.column.field].text), 1)
          ]),
          _: 1
        }, 8, ["href", "css-classes", "new-tab", "size", "variant"])
      ])) : vue.createCommentVNode("", true);
    }
  }), vt = { key: 0 }, bt = ["href", "target"], yt = /* @__PURE__ */ vue.defineComponent({
    __name: "DDVLink",
    props: {
      item: {},
      column: {}
    },
    setup(i) {
      return (t2, o) => t2.item[t2.column.field] ? (vue.openBlock(), vue.createElementBlock("span", vt, [
        vue.createElementVNode("a", {
          href: t2.item[t2.column.field].link,
          class: vue.normalizeClass(t2.column.classes),
          target: t2.item[t2.column.field].new_tab ? "_blank" : "_self"
        }, vue.toDisplayString(t2.item[t2.column.field].text), 11, bt)
      ])) : vue.createCommentVNode("", true);
    }
  }), _t = ["innerHTML"], $t = /* @__PURE__ */ vue.defineComponent({
    __name: "DDVHTML",
    props: {
      item: {},
      column: {}
    },
    setup(i) {
      return (t2, o) => (vue.openBlock(), vue.createElementBlock("span", {
        innerHTML: t2.item[t2.column.field]
      }, null, 8, _t));
    }
  }), kt = {
    key: 0,
    class: "dropdown"
  }, zt = /* @__PURE__ */ vue.createStaticVNode('<button class="btn p-1" type="button" data-bs-toggle="dropdown" aria-expanded="false" style="line-height:1rem;"><svg width="16px" height="16px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 13.75C12.9665 13.75 13.75 12.9665 13.75 12C13.75 11.0335 12.9665 10.25 12 10.25C11.0335 10.25 10.25 11.0335 10.25 12C10.25 12.9665 11.0335 13.75 12 13.75Z" fill="#000000"></path><path d="M19 13.75C19.9665 13.75 20.75 12.9665 20.75 12C20.75 11.0335 19.9665 10.25 19 10.25C18.0335 10.25 17.25 11.0335 17.25 12C17.25 12.9665 18.0335 13.75 19 13.75Z" fill="#000000"></path><path d="M5 13.75C5.9665 13.75 6.75 12.9665 6.75 12C6.75 11.0335 5.9665 10.25 5 10.25C4.0335 10.25 3.25 11.0335 3.25 12C3.25 12.9665 4.0335 13.75 5 13.75Z" fill="#000000"></path></svg></button>', 1), St = { class: "dropdown-menu" }, wt = {
    key: 0,
    class: "dropdown-divider"
  }, Ct = ["href", "target"], Bt = /* @__PURE__ */ vue.defineComponent({
    __name: "DDVActions",
    props: {
      item: {},
      column: {}
    },
    setup(i) {
      const t2 = i, o = vue.computed(() => t2.item[t2.column.field].entries());
      return (n, e) => o.value ? (vue.openBlock(), vue.createElementBlock("div", kt, [
        zt,
        vue.createElementVNode("ul", St, [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(o.value, ([l, a]) => (vue.openBlock(), vue.createElementBlock("li", { key: l }, [
            a.divider ? (vue.openBlock(), vue.createElementBlock("hr", wt)) : (vue.openBlock(), vue.createElementBlock("a", {
              key: 1,
              href: a.link,
              class: vue.normalizeClass(["dropdown-item", a.classes ?? ""]),
              target: a.new_tab ? "_blank" : "_self"
            }, vue.toDisplayString(a.text), 11, Ct))
          ]))), 128))
        ])
      ])) : vue.createCommentVNode("", true);
    }
  }), Vt = /* @__PURE__ */ vue.defineComponent({
    __name: "DDVColumn",
    props: {
      item: {},
      column: {}
    },
    setup(i) {
      return (t2, o) => t2.column.type == "string" ? (vue.openBlock(), vue.createBlock(mt, {
        key: 0,
        item: t2.item,
        column: t2.column
      }, null, 8, ["item", "column"])) : t2.column.type == "date" ? (vue.openBlock(), vue.createBlock(ft, {
        key: 1,
        item: t2.item,
        column: t2.column
      }, null, 8, ["item", "column"])) : t2.column.type == "button" ? (vue.openBlock(), vue.createBlock(ht, {
        key: 2,
        item: t2.item,
        column: t2.column
      }, null, 8, ["item", "column"])) : t2.column.type == "link" ? (vue.openBlock(), vue.createBlock(yt, {
        key: 3,
        item: t2.item,
        column: t2.column
      }, null, 8, ["item", "column"])) : t2.column.type == "html" ? (vue.openBlock(), vue.createBlock($t, {
        key: 4,
        item: t2.item,
        column: t2.column
      }, null, 8, ["item", "column"])) : t2.column.type == "actions" ? (vue.openBlock(), vue.createBlock(Bt, {
        key: 5,
        item: t2.item,
        column: t2.column
      }, null, 8, ["item", "column"])) : vue.createCommentVNode("", true);
    }
  }), Dt = /* @__PURE__ */ vue.defineComponent({
    __name: "DDVRow",
    props: {
      item: {},
      columns: {}
    },
    setup(i) {
      return (t2, o) => (vue.openBlock(), vue.createElementBlock("tr", null, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(t2.columns, (n) => (vue.openBlock(), vue.createElementBlock("td", {
          key: n.field,
          class: "align-middle"
        }, [
          vue.createVNode(Vt, {
            column: n,
            item: t2.item
          }, null, 8, ["column", "item"])
        ]))), 128))
      ]));
    }
  }), Ut = {
    key: 0,
    class: "alert alert-info w-100"
  }, Lt = { key: 0 }, Ot = { key: 1 }, It = ["colspan"], oe = /* @__PURE__ */ vue.defineComponent({
    __name: "DataDefinedVisualizer",
    props: {
      data: { default: null },
      columns: {},
      isLoading: { type: Boolean, default: false }
    },
    setup(i) {
      const t2 = i, o = vue.computed(() => t2.data === null || t2.data === void 0 || t2.data.length === 0), { t: n } = vueI18n.useI18n();
      return (e, l) => e.isLoading && o.value ? (vue.openBlock(), vue.createElementBlock("div", Ut, vue.toDisplayString(vue.unref(n)("loading")), 1)) : (vue.openBlock(), vue.createElementBlock("table", {
        key: 1,
        class: vue.normalizeClass(["table", e.isLoading ? "loading" : ""])
      }, [
        vue.createElementVNode("thead", null, [
          vue.createElementVNode("tr", null, [
            (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(e.columns, (a) => (vue.openBlock(), vue.createElementBlock("th", {
              key: a.field
            }, vue.toDisplayString(a.label), 1))), 128))
          ])
        ]),
        o.value ? (vue.openBlock(), vue.createElementBlock("tbody", Ot, [
          vue.createElementVNode("tr", null, [
            vue.createElementVNode("td", {
              colspan: e.columns.length
            }, vue.toDisplayString(vue.unref(n)("no_data")), 9, It)
          ])
        ])) : (vue.openBlock(), vue.createElementBlock("tbody", Lt, [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(e.data, (a) => (vue.openBlock(), vue.createBlock(Dt, {
            key: a.id,
            item: a,
            columns: e.columns
          }, null, 8, ["item", "columns"]))), 128))
        ]))
      ], 2));
    }
  });
  function J(i) {
    const t2 = i;
    t2.__i18n = t2.__i18n || [], t2.__i18n.push({
      locale: "",
      resource: {
        en: {
          loading: (o) => {
            const { normalize: n } = o;
            return n(["Loading...."]);
          },
          no_data: (o) => {
            const { normalize: n } = o;
            return n(["No items to display"]);
          }
        },
        nl: {
          loading: (o) => {
            const { normalize: n } = o;
            return n(["Gegevens worden laden..."]);
          },
          no_data: (o) => {
            const { normalize: n } = o;
            return n(["Geen gegevens om te tonen"]);
          }
        }
      }
    });
  }
  typeof J == "function" && J(oe);
  const Ft = /* @__PURE__ */ vue.defineComponent({
    __name: "DSCList",
    props: {
      config: {}
    },
    setup(i) {
      const t2 = i, o = vue.ref(t2.config.pageSize), n = vue.ref(1), e = vue.ref(""), l = vue.ref("id"), a = vue.ref(true);
      function u() {
        var m;
        let p = {};
        return (m = t2.config.filters) == null || m.forEach((k) => {
          var O;
          if (k.initial) {
            p[k.field] = k.initial;
            return;
          }
          switch (k.type) {
            case "date":
              p[k.field] = null;
              break;
            case "checkbox":
              p[k.field] = [];
              break;
            case "radio":
              ((O = k.options) == null ? void 0 : O.length) != 0 && k.options && (p[k.field] = k.options[0][0]);
              break;
          }
        }), p;
      }
      const _ = vue.ref(u());
      let y = vue.ref(null);
      const P = vue.computed(() => {
        let p = [];
        p.push("page_size=" + encodeURIComponent(o.value));
        for (const [m, k] of Object.entries(_.value))
          k != null && (typeof k == "object" ? k.forEach(
            (O) => p.push(m + "=" + encodeURIComponent(O))
          ) : p.push(m + "=" + encodeURIComponent(k)));
        return e.value && p.push("search=" + encodeURIComponent(e.value)), p.push("ordering=" + encodeURIComponent(l.value)), n.value = 1, p;
      }), I = vue.computed(() => {
        let p = P.value, m = "page=" + encodeURIComponent(n.value);
        return p.length !== 0 && (m = "&" + m), "?" + p.join("&") + m;
      }), U = vue.computed(() => {
        let p = new URL(window.location.protocol + "//" + window.location.host);
        return p.pathname = t2.config.dataUri, p.search = I.value, console.log(p.toString()), p.toString();
      });
      vue.watch(U, () => {
        F();
      });
      const $ = vue.ref(null);
      function F() {
        $.value && $.value.abort(), $.value = new AbortController(), a.value = true, fetch(U.value, { signal: $.value.signal }).then((p) => {
          p.json().then((m) => {
            y.value = m, a.value = false, m.ordering && (l.value = m.ordering), $.value = null;
          });
        }).catch((p) => {
          console.log(p);
        });
      }
      return vue.onMounted(() => {
        F();
      }), (p, m) => {
        var k, O, Z;
        return vue.openBlock(), vue.createBlock(ct, {
          "is-loading": a.value,
          data: ((k = vue.unref(y)) == null ? void 0 : k.results) ?? void 0,
          "total-data": ((O = vue.unref(y)) == null ? void 0 : O.count) ?? 0,
          "search-enabled": p.config.searchEnabled,
          search: e.value,
          "sort-enabled": p.config.sortEnabled,
          "current-sort": l.value,
          "page-size-options": p.config.pageSizeOptions,
          "sort-options": p.config.sortOptions ?? [],
          "page-size": ((Z = vue.unref(y)) == null ? void 0 : Z.page_size) ?? 10,
          "current-page": n.value,
          "filters-enabled": p.config.filtersEnabled,
          filters: p.config.filters ?? [],
          "filter-values": _.value,
          container: p.config.container,
          "onUpdate:search": m[0] || (m[0] = (C) => e.value = C),
          "onUpdate:currentSort": m[1] || (m[1] = (C) => l.value = C),
          "onUpdate:pageSize": m[2] || (m[2] = (C) => o.value = C),
          "onUpdate:currentPage": m[3] || (m[3] = (C) => n.value = C),
          "onUpdate:filterValues": m[4] || (m[4] = (C) => _.value = C)
        }, {
          data: vue.withCtx(({ data: C, isLoading: G }) => [
            vue.renderSlot(p.$slots, "data", {
              data: C,
              isLoading: G
            }, () => [
              vue.createVNode(oe, {
                data: C,
                columns: p.config.columns,
                "is-loading": G
              }, null, 8, ["data", "columns", "is-loading"])
            ])
          ]),
          _: 3
        }, 8, ["is-loading", "data", "total-data", "search-enabled", "search", "sort-enabled", "current-sort", "page-size-options", "sort-options", "page-size", "current-page", "filters-enabled", "filters", "filter-values", "container"]);
      };
    }
  });
  function block0(Component) {
    const _Component = Component;
    _Component.__i18n = _Component.__i18n || [];
    _Component.__i18n.push({
      "locale": "",
      "resource": {
        "en": {
          "name": (ctx) => {
            const { normalize: _normalize } = ctx;
            return _normalize(["Name"]);
          },
          "refnum": (ctx) => {
            const { normalize: _normalize } = ctx;
            return _normalize(["Reference Number"]);
          },
          "status": (ctx) => {
            const { normalize: _normalize } = ctx;
            return _normalize(["Status"]);
          }
        },
        "nl": {
          "name": (ctx) => {
            const { normalize: _normalize } = ctx;
            return _normalize(["Naam"]);
          },
          "refnum": (ctx) => {
            const { normalize: _normalize } = ctx;
            return _normalize(["Referentie Nummer"]);
          },
          "status": (ctx) => {
            const { normalize: _normalize } = ctx;
            return _normalize(["Status"]);
          }
        }
      }
    });
  }
  const _hoisted_1 = { key: 0 };
  const _hoisted_2 = {
    key: 1,
    class: "table"
  };
  const _sfc_main = {
    __name: "CustomList",
    props: ["config"],
    setup(__props) {
      const { t: t2 } = vueI18n.useI18n();
      function statusColor(status) {
        switch (status) {
          case "C":
            return "green";
          case "R":
            return "orange";
          case "O":
            return "red";
          default:
            return "";
        }
      }
      return (_ctx, _cache) => {
        return vue.openBlock(), vue.createBlock(vue.unref(Ft), { config: __props.config }, {
          data: vue.withCtx(({ data, isLoading }) => [
            vue.createElementVNode("div", null, [
              isLoading ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_1, " Loading... ")) : (vue.openBlock(), vue.createElementBlock("table", _hoisted_2, [
                vue.createElementVNode("thead", null, [
                  vue.createElementVNode("tr", null, [
                    vue.createElementVNode("th", null, vue.toDisplayString(vue.unref(t2)("name")), 1),
                    vue.createElementVNode("th", null, vue.toDisplayString(vue.unref(t2)("refnum")), 1),
                    vue.createElementVNode("th", null, vue.toDisplayString(vue.unref(t2)("status")), 1)
                  ])
                ]),
                vue.createElementVNode("tbody", null, [
                  (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(data, (datum) => {
                    return vue.openBlock(), vue.createElementBlock("tr", null, [
                      vue.createElementVNode("td", null, vue.toDisplayString(datum.project_name), 1),
                      vue.createElementVNode("td", null, vue.toDisplayString(datum.reference_number), 1),
                      vue.createElementVNode("td", {
                        class: vue.normalizeClass(`text-bg-${statusColor(datum.status)}`)
                      }, vue.toDisplayString(datum.get_status_display), 3)
                    ]);
                  }), 256))
                ])
              ]))
            ])
          ]),
          _: 1
        }, 8, ["config"]);
      };
    }
  };
  if (typeof block0 === "function")
    block0(_sfc_main);
  const style = "";
  return _sfc_main;
}(Vue, VueI18n);
