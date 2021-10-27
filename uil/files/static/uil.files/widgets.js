$(function () {
    let cont =  $('.uil-files-select-container');
    cont.on('setup', function () {
        let el = this; // Alias this, so we can use it in methods

        // Prevent multiple triggering on this element
        if (typeof (el.setup) !== "undefined")
            return;
        el.setup = true;

        let jq_el = $(el);

        el.name = jq_el.data('name');
        el.filenameEl = jq_el.find('.uil-files-filename');
        el.noFileText = el.filenameEl.html(); // By default it's filled with this text
        el.changedInput = jq_el.find('input[name="'+ el.name +'_changed"]')
        el.removeEl = jq_el.find('.uil-files-remove');
        el.selectEl = jq_el.find('.uil-files-select');
        el.selectLabel = $(el.selectEl).find('label');
        el.selectInput = $(el.selectEl).find('input[type="file"]');

        el.showSelect = function (filename="") {
            el.removeEl.hide();
            if (filename !== "") {
                el.filenameEl.html(filename);
            }
            el.selectEl.show();
        }
        el.showFile = function (filename="", url="") {
            el.selectEl.hide();
            if (filename !== "") {
                if (url !== "") {
                    el.filenameEl.html(
                        '<a href="'+url+'" target="_blank">' + filename + '</a>'
                    );
                } else {
                    el.filenameEl.html(filename);
                }
            }
            el.removeEl.show();
        }

        if (jq_el.data('filename') !== "") {
            el.showFile(jq_el.data('filename'), jq_el.data("url"));
        }

        el.removeEl.click(function () {
            el.changedInput.val(1);
            el.showSelect(el.noFileText);
        })

        el.selectLabel.click(function () {
            el.selectInput.trigger('click');
        });

        el.selectInput.on('input', function () {
            if($(this).val() != "") {
                el.showFile(this.files[0].name)
                el.changedInput.val(1);
            }
        });
    });

    cont.trigger('setup');
});