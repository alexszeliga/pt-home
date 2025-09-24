let map;
let styles = getComputedStyle(document.documentElement);
const primaryColor = styles.getPropertyValue('--color-primary')
const accentColor = styles.getPropertyValue('--color-secondary')
const primaryColorB = styles.getPropertyValue('--color-primary-content')
const accentColorB = styles.getPropertyValue('--color-secondary-content')

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
            background: location.is_default ? primaryColor : accentColor,
            borderColor: location.is_default ? primaryColorB : accentColorB,
            glyphColor: location.is_default ? primaryColorB : accentColorB,
            scale: 0.8
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