function update_info() {
    $.get("/Info", function (data) {
      // Actualizar los elementos HTML con los datos del paciente
      var result = JSON.parse(data);
      $("#i_d").html("Last ID:");
      $("#I_D").html(result.id);
      $("#Last").html("Last Updated:");
      $("#last").html(result );
      $("#Family").html("Family:");
      $("#family").html(result.name[0].family);
      $("#Phone").html("Phone:");
      $("#phone").html(result.telecom[0].value);
      $("#birthDate").html("BirthDate:");
      $("#birthdate").html(result.birthDate);
      $("#Email").html("Email:");
      $("#email").html(result.telecom[1].value);
      $("#Address").html("Address:");
      $("#address").html(result.address[0].line[0]);

      //document.getElementById("INFO").innerHTML = "<pre>" + jsonString + "</pre>";

    
    });
}

update();
var intervalId = setInterval(function () {
  update_info();
}, 1000);S
