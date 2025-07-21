(function () {
    'use strict'
  
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const forms = document.querySelectorAll('.needs-validation');
  
    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
      .forEach(function (form) {
        form.addEventListener('submit', function (event) {
          if (!form.checkValidity()) {
            event.preventDefault()
            event.stopPropagation()
          }
  
          form.classList.add('was-validated')
        }, false)
      })
  })()


  // Add active class to the current button (highlight it)
  const header = document.getElementById("ournavbar");
  const btns = header.getElementsByClassName("nav-item");
  for (const btn of btns) {
    btn.addEventListener("click", function() {
      const current = document.getElementsByClassName("active");
      if (current.length > 0) {
    current[0].className = current[0].className.replace(" active", "");
      }
    this.className += " active";
    });
  }


  $(function () {
    $('[data-toggle="tooltip"]').tooltip()
  })