// static/js/app.js
(function () {
  // --- Toggle campos conductor ---
  const rolesSel =
    document.getElementById("roles") ||
    document.querySelector('select[name="roles"]');

  const conductorBox = document.getElementById("conductor-fields");
  const lic = document.getElementById("licencia");
  const hoja = document.getElementById("hoja_vida_conduct");

  function isConductorSelected() {
    if (!rolesSel) return false;

    // Si el value del select es el nombre del rol (ej: "Conductor")
    const val = (rolesSel.value || "").toLowerCase().trim();
    if (val === "conductor") return true;

    // Alternativa: revisar el texto visible seleccionado
    const txt =
      (rolesSel.options?.[rolesSel.selectedIndex]?.text || "")
        .toLowerCase()
        .trim();

    return txt === "conductor";
  }

  function updateConductorFields() {
    if (!conductorBox) return;

    const show = isConductorSelected();
    conductorBox.style.display = show ? "" : "none";

    if (lic) lic.required = show;
    if (hoja) hoja.required = show;
  }

  if (rolesSel) {
    rolesSel.addEventListener("change", updateConductorFields);
    updateConductorFields();
  }

  // --- Cargar ciudades según país ---
  const paisSel =
    document.getElementById("pais") ||
    document.querySelector('select[name="pais"]');

  const ciudadSel =
    document.getElementById("ciudad") ||
    document.querySelector('select[name="ciudad"]');

  async function loadCities(paisId) {
    if (!ciudadSel) return;

    ciudadSel.innerHTML = '<option value="">Cargando ciudades...</option>';

    try {
      const res = await fetch(
        `/api/cities?id_pais=${encodeURIComponent(paisId)}`,
        {
          headers: { Accept: "application/json" }, // importante
        }
      );

      if (!res.ok) {
        ciudadSel.innerHTML =
          '<option value="">Error al cargar ciudades</option>';
        return;
      }

      const json = await res.json();

      // ✅ Tu API devuelve una LISTA directa: [{id, nombre_ciudad}, ...]
      const data = Array.isArray(json) ? json : (json.data || []);

      ciudadSel.innerHTML =
        '<option value="">Seleccione una ciudad...</option>';

      for (const c of data) {
        const opt = document.createElement("option");
        opt.value = c.id;
        opt.textContent = c.nombre_ciudad; // OJO: tu key se llama nombre_ciudad
        ciudadSel.appendChild(opt);
      }
    } catch (e) {
      ciudadSel.innerHTML = '<option value="">Error al cargar ciudades</option>';
    }
  }

  if (paisSel && ciudadSel) {
    paisSel.addEventListener("change", () => {
      const id = paisSel.value;
      if (id) loadCities(id);
      else ciudadSel.innerHTML =
        '<option value="">Seleccione una ciudad...</option>';
    });

    // Si ya viene país pre-seleccionado, carga al entrar
    if (paisSel.value) loadCities(paisSel.value);
  }
})();

// //darle vida al boton entrar
// document.addEventListener("DOMContentLoaded", function () {
//   const togglePassword = document.querySelector("#togglePassword");
//   const password = document.querySelector("#password");
//   if (togglePassword && password) {
//     togglePassword.addEventListener("click", function () {
//       // toggle the type attribute
//       const type =
//         password.getAttribute("type") === "password" ? "text" : "password";
//       password.setAttribute("type", type);
//       // toggle the eye slash icon
//       this.classList.toggle("fa-eye-slash");
//     });
//   }
// });

// Agregar funcionalidad al botón de mostrar/ocultar contraseña

(function () {
  const input = document.getElementById('password');
  const btn = document.getElementById('togglePwd');
  const icon = document.getElementById('togglePwdIcon');
  if (!input || !btn || !icon) return;
  btn.addEventListener('click', function () {
    const isText = input.type === 'text';
    input.type = isText ? 'password' : 'text';
    icon.classList.toggle('bi-eye', isText);
    icon.classList.toggle('bi-eye-slash', !isText);
  });
})();

// Evitar navegar atrás en páginas autenticadas y preguntar por cerrar sesión
(function () {
  const body = document.body;
  if (!body) return;
  // Detectar sesión: por presencia del formulario oculto de logout o por data-logged-in
  const hasLogoutForm = !!document.getElementById('logoutForm');
  const isLoggedInAttr = body.getAttribute('data-logged-in') === '1';
  const isLoggedIn = hasLogoutForm || isLoggedInAttr;
  if (!isLoggedIn) return;

  // Empujar estado inicial para que el back dispare popstate
  try {
    history.pushState(null, document.title, location.href);
  } catch (e) {}

  window.addEventListener('popstate', function (e) {
    // Si SweetAlert2 está disponible, usarlo; de lo contrario, fallback a confirm()
    if (window.Swal && typeof window.Swal.fire === 'function') {
      window.Swal.fire({
        title: '¿Cerrar sesión?',
        text: 'Para volver al login, debes cerrar tu sesión.',
        icon: 'Danger',
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: 'Sí',
        cancelButtonText: 'Cancelar'
        
      }).then((result) => {
        if (result.isConfirmed) {
          const form = document.getElementById('logoutForm');
          if (form) form.submit();
        } else {
          try { history.pushState(null, document.title, location.href); } catch (e) {}
        }
      });
    } else {
      const confirmLogout = window.confirm('¿Desea cerrar la sesión?');
      if (confirmLogout) {
        const form = document.getElementById('logoutForm');
        if (form) form.submit();
      } else {
        try { history.pushState(null, document.title, location.href); } catch (e) {}
      }
    }
  });
})();
