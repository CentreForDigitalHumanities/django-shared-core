/**
 * Quick helper to configure tinyMCE using data-attributes
 * Needed for the widget to work with CSP enabled, as widgets cannot contain JS itself with CSP enabled
 */
$(function () {
    const els = $('textarea[data-tinymce]');

    els.each((i, el) => {
        let element = $(el)

        let menubar = element.data('menubar') || false;
        let plugins = element.data('plugins');
        let toolbar = element.data('toolbar');
        let language = element.data('language') || 'nl';

        if (plugins === undefined)
            plugins = [
                'link', 'image', 'visualblocks', 'wordcount', 'lists', 'code',
            ]
        else
            plugins = plugins.split(',')

        if (toolbar === undefined)
            toolbar = 'undo redo | casechange blocks | bold italic underline | link | bullist numlist | code'

        element.tinymce({
            height: 500,
            menubar,
            plugins,
            toolbar,
            language,
          });
    })
})
