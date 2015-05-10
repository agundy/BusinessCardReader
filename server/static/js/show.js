var fields = ['Name', 'Title','Company', 'Address', 'Email', 'Cell', 'Phone']

fields.forEach(function(field){
    $('.fields').append("<input value='" + field+ "' type='button'>");
});

var addData = function(card){
    card.text.forEach(function(paragraph){
        console.log(paragraph);
        paragraph.forEach(function(line){
            $('.text').append('<tr> <td>Check</td> <td>' + line + '</td> <td></td> </tr>');
        });
    });
};

var checkForCard = function(){
    $.getJSON('/api/card/' + card_id, function(card){
        if (card.processed){
            addData(card);
            clearInterval(refreshIntervalId);
        }
    });
};

var refreshIntervalId = setInterval(checkForCard, 500);
