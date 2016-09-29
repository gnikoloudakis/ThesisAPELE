/**
 * Created by yannis on 4/21/2016.
 */

var map, infowindow, marker, circle;


function create_map(user_location) {
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 10,
        center: new google.maps.LatLng(user_location[0], user_location[1]),
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });
}

function set_user_marker(user_location, radius) {
    marker = new google.maps.Marker({
        position: new google.maps.LatLng(user_location[0], user_location[1]),
        map: map,
        icon: 'http://maps.google.com/mapfiles/kml/paddle/red-circle.png'
    });
    var center = new google.maps.LatLng(user_location[0],user_location[1])
    circle = new google.maps.Circle({
        center: center,
        radius: 1000,
        strokeColor: "#FF0000",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#FF0000",
        fillOpacity: 0.35,
        map: map
    });
}
function set_markers(locations) {
    infowindow = new google.maps.InfoWindow();

    var i;

    for (i = 0; i < locations.length; i++) {
        marker = new google.maps.Marker({
            position: new google.maps.LatLng(locations[i][1], locations[i][2]),
            map: map,
            icon: 'http://maps.google.com/mapfiles/kml/paddle/blu-circle.png'
        });

        google.maps.event.addListener(marker, 'click', (function (marker, i) {
            return function () {
                infowindow.setContent(locations[i][0]);
                infowindow.open(map, marker);
            }
        })(marker, i));
    }
}

function create_multimap(unsafe_user, user_lng, user_lat, volunteer_list, map_id) {
    var map, circle;
    map = new google.maps.Map(document.getElementById(map_id), {
        zoom: 10,
        center: new google.maps.LatLng(user_lat, user_lng),   //set unsafe user location
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    var infowindow = new google.maps.InfoWindow();

    var unsafe_user_marker, marker, i;
    marker = new google.maps.Marker({
        position: new google.maps.LatLng(user_lat, user_lng),
        icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
        map: map
    }); // unsafe user position

    var center = new google.maps.LatLng(user_lat,user_lng)
    circle = new google.maps.Circle({
        center: center,
        radius: 1000,
        strokeColor: "#FF0000",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#FF0000",
        fillOpacity: 0.35,
        map: map
    });

    google.maps.event.addListener(marker, 'click', (function (marker, i) { // volunteers info
        return function () {
            infowindow.setContent('MISSING USER ' + unsafe_user);
            infowindow.open(map, marker);
        }
    })(marker, i));
    ////////////////////////////////////////////////////////////////////////

    for (i = 0; i < volunteer_list.length; i++) { //volunteers positions
        marker = new google.maps.Marker({
            position: new google.maps.LatLng(volunteer_list[i][4], volunteer_list[i][3]),
            icon: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
            map: map
        });

        google.maps.event.addListener(marker, 'click', (function (marker, i) { // volunteers info
            return function () {
                infowindow.setContent('VOLUNTEER\n First Name: ' + volunteer_list[i][0] + 'Last Name: ' + volunteer_list[i][1] + 'E-mail: ' + volunteer_list[i][2]);
                infowindow.open(map, marker);
            }
        })(marker, i));
    }
}