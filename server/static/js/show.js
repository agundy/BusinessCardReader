var fields = ['Name', 'Title','Company', 'Address', 'Email', 'Cell', 'Phone', 'Website', 'Fax']
var card = null;

// Handles creation and making of field buttons
fields.forEach(function(field){
    var button = "<input value='" + field+ "' id='" + field + "' onClick=\x22selectField('" + field + "')\x22 class='fieldBtn' type='button'>";
    $('.fields').append(button);
});

var addField = function(suggestedField, line){
    $('.edit') .append("<div class='row'>" +
            "<div class='twelve columns'>" + 
            "<label for='name'>" + suggestedField  + "</label>" + 
            "<input class='u-full-width' id='name' value='" + line + "' type='text'>"+
            "</div></div>");
}

var addData = function(card){
    var cardImage = document.getElementById('processedImg').src = '/static/processed/' + card.filename;
    $('#uploadedImg').addClass("hidden");
    $("#processedImg").removeClass("hidden");
    $("#uploadedBtn").removeClass("button-primary");
    $('#processedBtn').addClass("button-primary");
    for (var i = 0; i < card.text.length; i++){
        var paragraph = card.text[i];
        for (var j = 0; j < paragraph.length; j++){
            var line = paragraph[j];
            var suggestedField = card.suggested[i][j];

            $('.text').append("<tr> <td><input type='checkbox' name='checkbox' value='" + line + "'></td> <td>" + line + "</td> <td>" + suggestedField + "</td> </tr>");
            if (suggestedField != ''){
                addField(suggestedField, line)
            }
        }
    }
    if (card.warnings.length > 0){
        card.warnings.forEach(function(warning){
            $('.warning').append(warning);
        });
    } else{
        $('.warning').append('No errors detected');
    }

    card.text.forEach(function(paragraph){
        paragraph.forEach(function(line){
        });
    });
};

var checkForCard = function(){
    $.getJSON('/api/card/' + card_id, function(card){
        card = card;
        if (card.processed){
            clearInterval(refreshIntervalId);
            addData(card);
        }
    });
};

var refreshIntervalId = setInterval(checkForCard, 500);

$("#uploadedBtn").click(function(){
    $('#processedImg').addClass("hidden");
    $("#uploadedImg").removeClass("hidden");
    $("#processedBtn").removeClass("button-primary");
    $('#uploadedBtn').addClass("button-primary");
});

$("#processedBtn").click(function(){
    $('#uploadedImg').addClass("hidden");
    $("#processedImg").removeClass("hidden");
    $("#uploadedBtn").removeClass("button-primary");
    $('#processedBtn').addClass("button-primary");
});

var selectedBtn = '';

var selectField = function(name){
    $(".fieldBtn").removeClass("button-primary");
    $("#" + name).addClass("button-primary");
    selectedBtn = name;
}

var joinFields = function(){
    // TODO Add functionality for joining fields
}

var tagField = function(){
    // var value = $("input[type=checkbox]:checked").value();
    var text = '';
    $('input[name="checkbox"]:checked').each(function() {
        text = this.value;
        $(this).removeAttr('checked');
    });
    if (text != '' && selectedBtn != ''){
        addField(selectedBtn, text);
    }
}129.161.33.95
