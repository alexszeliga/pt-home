let map;
let styles = getComputedStyle(document.documentElement);
const primaryColor = styles.getPropertyValue('--color-primary')
const accentColor = styles.getPropertyValue('--color-secondary')
const primaryColorB = styles.getPropertyValue('--color-primary-content')
const accentColorB = styles.getPropertyValue('--color-secondary-content')

async function initMap() {
    const addressData = document.querySelector('#address-data').dataset
    const septaData = [...document.querySelectorAll('[id^="stop_"]')].map((node)=>node.dataset)
    const position = { lat: parseFloat(addressData.lat) ?? -25.344, lng: parseFloat(addressData.lng) ?? 131.031 };
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement, PinElement } = await google.maps.importLibrary("marker");

    const map = new Map(document.getElementById("map-wrapper"), {
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

    var infoWindow = new google.maps.InfoWindow();

    septaData.forEach((location,i) => {
        const pin = new PinElement({
            background: location.is_default ? primaryColor : accentColor,
            borderColor: location.is_default ? primaryColorB : accentColorB,
            glyphColor: location.is_default ? primaryColorB : accentColorB,
            scale: 0.8
        })

        const position = {lat: parseFloat(location.lat), lng: parseFloat(location.lng)}

        const marker = new AdvancedMarkerElement({
            map:map,
            position:position,
            title: location.name,
            content: pin.element,
        })

        marker.addListener('click', ()=>{
            infoWindow.setHeaderDisabled(true)
            infoWindow.setContent(`
                <button id="close_button_${location.id}" class="p-2 rounded-full bg-gray-200 hover:bg-gray-300 text-gray-700">
                    <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
                <h2 class="text-lg">${location.name}</h2>
                <button class="btn btn-primary" id="button_${location.id}">Set as Default</button>
            `)
            infoWindow.open(map, marker)
        })
    })

    document.body.addEventListener('click', function(event) {
        const clickedElement = event.target;
        const elementId = clickedElement.id;
        
        const elementRegex = /^button_/
        if (elementRegex.test(elementId)) {
            const data = document.querySelector(`#${elementId.replace('button','stop')}`).dataset
            const form = document.createElement('form')
            form.method = 'POST'
            form.action = window.location.href
            form.style.display = 'none'
            const field = document.createElement('input')
            field.type = 'hidden'
            field.name = 'default_septa_location'
            field.value = data.id
            const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].cloneNode(true)
            let routeField = document.getElementById('id_route').cloneNode(true)
            form.appendChild(csrf)
            form.appendChild(field)
            form.appendChild(routeField)
            document.body.appendChild(form)
            form.submit()
        }
        const closeRegex = /^close_button_/
        if (closeRegex.test(elementId) || closeRegex.test(clickedElement.parentElement.id) ||closeRegex.test(clickedElement.parentElement.parentElement.id)) {
            infoWindow.close()
        }
    
    });
}

initMap();