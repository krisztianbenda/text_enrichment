function sendDoc() {
    var switches = document.getElementsByClassName('entity-switch');
    var entities = [];
    for (i = 0; i < switches.length; i++) {
        if (switches[i].checked) {
            entities.push(switches[i].id.split('_')[1]);
        }
    }

    var dataJSON = {};
    if (document.getElementById("userDoc").value === "") {
        console.info('no doc to process');
    } else if (entities.length == 0) {
        console.info('no selected entity')
    } else {
        dataJSON['text'] = document.getElementById("userDoc").value;
        dataJSON['required_labels'] = entities;
        $.ajax({
            url: '/text-enrichment/new-doc',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(dataJSON),
            success: function (doc_id) {
                window.location.href = "http://127.0.0.1:5000/text-enrichment/" + doc_id;
            }
        });
    }

}