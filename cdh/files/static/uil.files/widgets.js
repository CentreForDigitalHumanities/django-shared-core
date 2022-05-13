$(function () {
    let cont =  $('.uil-files-select-container');
    cont.on('setup', function () {
        let el = this; // Alias this, so we can use it in methods
        el.name = $(el).data('name');
        el.filenameEl = $(el).find('.uil-files-filename');
        el.noFileText = el.filenameEl.html(); // By default it's filled with this text
        el.filenameInput = $(el).find('input[name="'+ el.name +'_filename"]')
        el.changedInput = $(el).find('input[name="'+ el.name +'_changed"]')
        el.removeEl = $(el).find('.uil-files-remove');
        el.selectEl = $(el).find('.uil-files-select');
        el.selectLabel = $(el.selectEl).find('label');
        el.selectInput = $(el.selectEl).find('input[type="file"]');

        el.showSelect = function (filename="") {
            el.removeEl.hide();
            if (filename !== "") {
                el.filenameEl.html(filename);
            }
            el.selectEl.show();
        }
        el.showFile = function (filename="") {
            el.selectEl.hide();
            if (filename !== "") {
                el.filenameEl.html(filename);
            }
            el.removeEl.show();
        }

        if (el.filenameInput.val() !== "") {
            el.showFile(el.filenameInput.val());
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