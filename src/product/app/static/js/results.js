function poll() {
    url = document.URL.split('/')
    doc_id = url[url.length-1]
    $.ajax({
        url: 'http://127.0.0.1:5000/api/'+doc_id,
        type: 'GET',
        success: function(data) {
            data = JSON.parse(data);
            if (data.status === 'in progress'){
                document.getElementById('doc').textContent = 'in progress';
                setTimeout(poll, 500);
            } else if(data.status === 'ready') {
                document.getElementById('doc').textContent = data.entities;
            }
        }
    });
    }



    window.onload = poll;