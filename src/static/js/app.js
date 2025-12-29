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