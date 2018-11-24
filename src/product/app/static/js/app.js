function sendDoc() {
    var dataJSON = {};
    if (document.getElementById("userDoc").value === "") {
        console.info('no doc to process');
    } else {
        dataJSON['text'] = document.getElementById("userDoc").value;
        $.ajax({
            url: '/text-enrichment/new-doc',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(dataJSON),
            success: function(doc_id) {
                window.location.href = "http://127.0.0.1:5000/text-enrichment/"+doc_id;
            }
        });
    }

}