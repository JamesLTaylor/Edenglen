var map;
var polygons = [];
var polygonsWithBorder = [];


function initMap() {
    var mapOptions = {
        disableDoubleClickZoom: true,
        zoom: 16,
        center: new google.maps.LatLng(-26.13446146639315, 28.172528743743896)
    };
    
    map = new google.maps.Map(document.getElementById('map'),
        mapOptions);
        
    google.maps.event.addListener(map, "zoom_changed", function() {
        if (map.getZoom() > 17) {
            removePolys(polygons);
            setPolys(polygonsWithBorder);
        }    
        else {
            removePolys(polygonsWithBorder);
            setPolys(polygons);
        }
    }); 
}

var infowindow = new google.maps.InfoWindow({
    content: "hello"
});

function makePolys() {     
    for (var i = 0; i < polygonData.length; i++) {
        arr = [];        
        for (var j=0; j < polygonData[i].coords.length; j++) {
            arr.push( new google.maps.LatLng(polygonData[i].coords[j][0], polygonData[i].coords[j][1] ) );
            //bounds.extend(arr[arr.length-1])
        }
        
        address = polygonData[i].address
        msg = polygonData[i].msg
        fill_color = polygonData[i].fill_color
        
        polygons.push(new google.maps.Polygon({
            paths: arr,            
            strokeColor: fill_color,
            strokeOpacity: 035,
            strokeWeight: 1,
            fillColor: fill_color,
            fillOpacity: 0.35
        }));
        polygonsWithBorder.push(new google.maps.Polygon({
            paths: arr,            
            strokeColor: '#000000',
            strokeOpacity: 0.8,
            strokeWeight: 1,
            fillColor: fill_color,
            fillOpacity: 0.35
        }));
        
        polygon = polygonsWithBorder[polygonsWithBorder.length-1]
        polygon.content = '<p><u>' + address + '</u></p><p>' + msg + '</p><p><a href="http://www.edenglensouthclosure.co.za">more information</a></p'
        polygon.addListener('click', function(event) {
            infowindow.setPosition(event.latLng);
            infowindow.setContent(this.content)
            infowindow.open(map, polygon);
        });        
    }
}

/**
* 
*/ 
function makeAndSetBoundingPoly()
{
    var arr = [];        
    for (var j=0; j < boundingPolygonData.length; j++) {
        arr.push( new google.maps.LatLng(boundingPolygonData[j][0], boundingPolygonData[j][1] ) );        
    }
    boundingPolygon = new google.maps.Polygon({
        paths: arr,            
        strokeColor: '#000000',
        strokeOpacity: 0.8,
        strokeWeight: 4,
        fillColor: '#000000',
        fillOpacity: 0
    });
    boundingPolygon.setMap(map)
}


function setPolys(polys)
{
    for (var i=0; i < polys.length; i++)
    {
        polys[i].setMap(map);
    }
}


function removePolys(polys)
{
    for (var i=0; i < polys.length; i++)
    {
        polys[i].setMap(null);
    }    
}