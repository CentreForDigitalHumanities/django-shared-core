function postToPopUp(url, windowoption, name, params) {
    let form = document.createElement("form");
    form.setAttribute("method", "post");
    form.setAttribute("action", url);
    form.setAttribute("target", name);
    for (let i in params) {
        if (params.hasOwnProperty(i)) {
            let input = document.createElement('input');
            input.type = 'hidden';
            input.name = i;
            input.value = params[i];
            form.appendChild(input);
        }
    }
    document.body.appendChild(form);
    window.open("post.htm", name, windowoption);
    form.submit();
    document.body.removeChild(form);
}

$(function () {

    tinymce.PluginManager.add('preview-mail', (editor, url) => {

        editor.ui.registry.addButton('preview-mail', {
            text: 'Preview Email',
            onAction: () => {
                let csrf = $('input[name="csrfmiddlewaretoken"]').val();

                let params = {
                    'contents': editor.getContent(),
                    'csrfmiddlewaretoken': csrf,
                }

                let textarea = $(editor.getElement());

                let previewUrl = textarea.data('preview-url');

                let senderField = textarea.data('sender-field');
                let bannerField = textarea.data('banner-field');
                let footerField = textarea.data('footer-field');

                if (senderField !== undefined)
                    params['sender'] = $("#id_" + senderField).val();
                if (bannerField !== undefined)
                    params['banner'] = $("#id_" + bannerField).val();
                if (footerField !== undefined)
                    params['footer'] = $("#id_" + footerField).val();

                postToPopUp(
                    previewUrl,
                    "width=1200, height=600, left=100, top=100, resizable=yes, scrollbars=yes",
                    "MailPreview",
                    params
                );
            }
        });

        return {
            name: 'preview-mail',
          };
    });

});
