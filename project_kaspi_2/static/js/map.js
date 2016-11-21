ymaps.ready()
    .done(function (ym) {
        var myMap = new ym.Map('map', {
            center: [43.237259, 76.915419],
            zoom: 13,
            controls:[],
        });

     

        var zoomControl = new ymaps.control.ZoomControl({
            options: {
                size: "large",
                position: {
                    left: 'auto',
                    right: 10,
                    top: 10,
                }
            }
        });
        myMap.controls.add(zoomControl);

        var geoObjects;

        $('#my-block').show();



        $("#my-search input").keyup(function(e){
            if($(this).val().length >= 3){    
                $('.my-hidden').show();
                if(e.which == 13 && geoObjects.getLength() != 0) {
                    $(".item").removeClass('selected');
                    $(".item:first-child").addClass('selected');
                    myMap.geoObjects.removeAll();
                    var id = 0;
                    point = geoObjects.get(id);
                    myMap.geoObjects.add(point);
                    myMap.setCenter(point.geometry._coordinates, 17,{duration: 1000});
                } else {
                    $("#my-list-items").html("<img src='/static/img/loading.gif'>"); 
                    jQuery.getJSON('/search', {'text': $(this).val()}, function (json) {
                        myMap.geoObjects.removeAll();
                        geoObjects = ym.geoQuery(json.data);
                        if(geoObjects.getLength() != 0){
                            var venue_list_html = ''
                            geoObjects.each(function(item, i){
                                item.properties.set('balloonContent', item.properties.get("street") + ", " + item.properties.get("house") + "<br>" + item.properties.get("district"));
                                venue_list_html += "<div class='item' id='"+i+"'><span class='glyphicon glyphicon-map-marker' aria-hidden='true'></span>" + item.properties.get("street") + ", " + item.properties.get("house") + "<br>" + item.properties.get("district") + '</div>';
                            });
                            $("#my-list-items").html(venue_list_html);

                            $(".item").click(function(){
                                $(".item").removeClass('selected');
                                $(this).addClass('selected');
                                myMap.geoObjects.removeAll();
                                var id = $(this).attr('id');
                                point = geoObjects.get(id);
                                myMap.geoObjects.add(point);
                                myMap.setCenter(point.geometry._coordinates, 17,{duration: 1000});
                            });    
                        } else {
                            $("#my-list-items").html("<h4>По вашему запросу ничего не найдено</h4>");
                        }
                        $("#my-count").html(geoObjects.getLength());
                    }).fail(function(){
                        $("#my-list-items").html("<h4>Проблемы с соединением</h4>"); 
                    });     
                }
            } else {
                $('.my-hidden').hide();
            }
        });

        $("#my-search-button").click(function(){
            if(geoObjects.getLength() != 0) {
                    $(".item").removeClass('selected');
                    $(".item:first-child").addClass('selected');
                    myMap.geoObjects.removeAll();
                    var id = 0;
                    point = geoObjects.get(id);
                    myMap.geoObjects.add(point);
                    myMap.setCenter(point.geometry._coordinates, 17,{duration: 1000});
            }
        });

        $("#my-clear").click(function(){
            $("#my-search input").val('');
            $("#my-search input").keyup();
        });

    });