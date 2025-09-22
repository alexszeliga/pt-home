async function initMap() {
  await google.maps.importLibrary("places");
  const inputElm = document.getElementById('gmp-input')
  const placeAutocomplete = new google.maps.places.PlaceAutocompleteElement();
  
  inputElm.appendChild(placeAutocomplete);

  const nameField = document.getElementById('id_name');
  const addressField = document.getElementById('id_address');
  const placeIdField = document.getElementById('id_place_id');
  const latitudeField = document.getElementById('id_latitude');
  const longitudeField = document.getElementById('id_longitude');
  const displayNameField = document.getElementById('id_display_name');

  const resultsWrapper = document.getElementById('gmp-result');
  const resultTemplate = document.getElementById('gmp-result-body');

  const updateFormFields = (fields) => {
    nameField.placeholder = fields.displayName;
    addressField.value = fields.formattedAddress
    placeIdField.value = fields.id
    latitudeField.value = fields.location.lat.toFixed(6)
    longitudeField.value = fields.location.lng.toFixed(6)
    displayNameField.value = fields.displayName;
  }

  const updateResults = (fields) => {
    const template = document.importNode(resultTemplate.content, true);
    template.querySelector('#result_display_name').textContent = fields.displayName;
    template.querySelector('#result_address').textContent = fields.formattedAddress;
    template.querySelector('#result_coord').textContent = `${fields.location.lat.toFixed(6)} / ${fields.location.lng.toFixed(6)}`
    resultsWrapper.replaceChildren(template);
  }

  placeAutocomplete.addEventListener('gmp-select', async ({ placePrediction }) => {
      const place = placePrediction.toPlace();

      await place.fetchFields({ fields: ['displayName', 'formattedAddress', 'location'] });
      const fields = place.toJSON();
      updateFormFields(fields);
      updateResults(fields);
  });

  inputElm.addEventListener('click', (e) => {

    console.log(e)
  })

}
initMap();