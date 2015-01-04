/*
search.js
Provides AJAX search funtionality on the home page.
*/


$('#search_form').submit(function(event) {
    event.preventDefault();
    do_search();
});

$('#search_field').keyup(function() {
    do_search();
});


function do_search()
{
    $('#search_results').fadeIn();
    var q = $('#search_field').val();
    $.getJSON('/search_ajax?q=' + q, function(data) {
        var t = data.cinemas.n + data.films.n;
        $('#search_results_number').html(t + ' results');
        
        if(data.cinemas.n > 0)
            $('#search_results_cinemas').fadeIn();
        else
            $('#search_results_cinemas').fadeOut();
        
        if(data.films.n > 0)
            $('#search_results_films').fadeIn();
        else
            $('#search_results_films').fadeOut();
        
        
        var cinemas = '';
        var films = '';
        
        var i;
        for(i=0; i<data.cinemas.results.length; i++) {
            var c = data.cinemas.results[i];
            cinemas += '<li><a target="blank" href="' + c.url + '">' + c.name + '</a></li>';
        }
        
        $('#search_results_cinemas_target').html(cinemas);
        
        for(i=0; i<data.films.results.length; i++) {
            var f = data.films.results[i];
            films += '<li><a href="/films/' + f.api_id + '">' + f.title + '</a></li>';
        }
        
        $('#search_results_films_target').html(films);
        
        
    });
}



