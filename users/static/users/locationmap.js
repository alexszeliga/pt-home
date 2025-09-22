let map;

async function initMap() {
    const addressData = document.querySelector('#address-data').dataset
    const septaData = [...document.querySelectorAll('[id^="septa_location_"]')].map((node)=>node.dataset)
    const position = { lat: parseFloat(addressData.lat) ?? -25.344, lng: parseFloat(addressData.lng) ?? 131.031 };
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement, PinElement } = await google.maps.importLibrary("marker");

    map = new Map(document.getElementById("map-wrapper"), {
        zoom: 17,
        center: position,
        mapId: '81ebb4528da22371e9ddfa87',
        colorScheme: google.maps.ColorScheme.FOLLOW_SYSTEM,
    });

    const marker = new AdvancedMarkerElement({
        map: map,
        position: position,
        title: addressData.name ?? "",
    });
    septaData.forEach((location) => {
        const pin = new PinElement({
            background: '#FF0000',
            borderColor: '#0000FF',
            glyphColor: '#FFFFFF',
            scale: 0.5
        })
        const position = {lat: parseFloat(location.lat), lng: parseFloat(location.lng)}
        new AdvancedMarkerElement({
            map:map,
            position:position,
            title: location.name,
            content: pin.element,
        })
    })
}

initMap();