var resultsAreReady = false;
var summaryIsReady = false;

function parseResults(text, entities) {
    parsedText = [];

    lastChar = 0;
    entities.forEach(entity => {
        if (lastChar != entity.start_char) {
            parsedText.push({ text: text.substring(lastChar, entity.start_char), etype: 'text' });
        }
        parsedText.push({ text: text.substring(entity.start_char, entity.end_char), etype: 'entity', params: entity });
        lastChar = entity.end_char;
    });
    parsedText.push({ text: text.substring(lastChar), etype: 'text' });

    return parsedText;
}

function generateResultText(parsedText) {
    result = document.createElement('div');
    result.className = 'results';
    document.getElementById('doc').appendChild(result);
    parsedText.forEach(fragment => {
        if ('text' === fragment.etype) {
            text = document.createElement('mark');
            text.className = 'entity-mark entity-text'
            text.innerText = fragment.text;
            result.appendChild(text);
        } else {
            mark = document.createElement('a');
            mark.className = 'entity-mark entity-' + fragment.params.label_name;
            mark.innerText = fragment.text;
            if ('Format is currently not supported' === fragment.params.link) {
                mark.className += ' invalid-link';
            } else {
                mark.href = fragment.params.link;
                mark.target = '_blank';
            }
            result.appendChild(mark);
            span = document.createElement('span');
            span.className = 'entity-span';
            span.innerText = fragment.params.label_name;
            mark.appendChild(span);
        }
    });
}

function poll() {
    url = document.URL.split('/')
    doc_id = url[url.length - 1]
    $.ajax({
        url: 'http://127.0.0.1:5000/text-enrichment/' + doc_id + '/results',
        type: 'GET',
        success: function (data) {
            data = JSON.parse(data);
            if (data.status === 'in progress') {
                setTimeout(poll, 500);
            } else if (data.status === 'processed') {
                generateResultText(parseResults(data.text, JSON.parse(data.entities)));
                resultsAreReady = true;
                document.getElementById('loader').className = 'hide';
            }
        }
    });
}

function generateSummary(data) {
    summary = document.createElement('ul');
    summary.className = 'vertical menu';
    document.getElementById('sum').appendChild(summary);

    data.labels.forEach(label => {
        li = document.createElement('li');
        summary.appendChild(li);
        h3 = document.createElement('h3');
        h3.innerText = '#' + label;
        h3.className = 'sum-entity-type sum-entity-' + label;
        li.appendChild(h3);
        ul = document.createElement('ul');
        ul.className = 'menu';
        li.appendChild(ul);
        data.summary[label].forEach(entity => {
            li2 = document.createElement('li')
            ul.appendChild(li2);
            a = document.createElement('a');
            a.className = 'sum-entity';
            if ('Format is currently not supported' === entity.link) {
                a.className += ' invalid-link';
            } else {
                a.href = entity.link;
                a.target = '_blank';
            }
            a.innerText = entity.expression;
            li2.appendChild(a);
        });
    });
}

function getSummary() {
    url = document.URL.split('/')
    doc_id = url[url.length - 1]
    $.ajax({
        url: 'http://127.0.0.1:5000/text-enrichment/' + doc_id + '/summary',
        type: 'GET',
        success: function (data) {
            data = JSON.parse(data);
            generateSummary(data);
            summaryIsReady = true;
            document.getElementById('results-container').className = 'hide';
            document.getElementById('summary-container').className = '';
            document.getElementById('loader').className = 'hide';
        }
    });
}

function showResults() {
    if (resultsAreReady) {
        document.getElementById('results-container').className = '';
        document.getElementById('summary-container').className = 'hide';
    }
}

function showSummary() {
    if (summaryIsReady) {
        document.getElementById('results-container').className = 'hide';
        document.getElementById('summary-container').className = '';
    } else {
        document.getElementById('loader').className = '';
        getSummary();
    }
}

function goBack() {
    window.location.href = "http://127.0.0.1:5000/text-enrichment";
}

window.onload = poll;