// =====================================
// GUARDAR USUARIO
// =====================================
document.getElementById('formUsuario')
.addEventListener('submit', async function(e){

    e.preventDefault();

    const data = {

        nombre_completo:
            document.getElementById('nombre_completo').value,

        usuario:
            document.getElementById('usuario').value,

        password:
            document.getElementById('password').value,

        rol:
            document.getElementById('rol').value,

        email:
            document.getElementById('email').value,

        telefono:
            document.getElementById('telefono').value

    };

    try {

        const res = await fetch('/api/usuarios/guardar', {

            method: 'POST',

            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify(data)

        });

        const json = await res.json();

        if(json.success){

            alert('✅ Usuario guardado');

            cargarUsuarios();

            document.getElementById('formUsuario').reset();

            bootstrap.Modal.getInstance(
                document.getElementById('modalUsuario')
            ).hide();

        } else {

            alert(json.error);

        }

    } catch(err){

        console.error(err);

        alert('Error del servidor');

    }

});

// =====================================
// EDITAR USUARIO
// =====================================
function editarUsuario(id, nombre_completo, usuario, rol, email, telefono){

    usuarioEditandoId = id;

    document.getElementById('nombre_completo').value = nombre_completo;
    document.getElementById('usuario').value         = usuario;
    document.getElementById('password').value        = '';
    document.getElementById('rol').value             = rol;
    document.getElementById('email').value           = email;
    document.getElementById('telefono').value        = telefono;

    // Cerrar modal de lista primero
    const modalLista = bootstrap.Modal.getInstance(
        document.getElementById('modalListaUsuarios')
    );

    if(modalLista) modalLista.hide();

    // Esperar que cierre y luego abrir el de formulario
    setTimeout(() => {
        const modalForm = new bootstrap.Modal(
            document.getElementById('modalUsuario')
        );
        modalForm.show();
    }, 300);

}


// =====================================
// CARGAR USUARIOS
// =====================================
async function cargarUsuarios(){

    try {

        const res = await fetch('/api/usuarios');

        const usuarios = await res.json();

        let html = '';

        usuarios.forEach(u => {

            html += `
                <tr>

                    <td>${u.id}</td>

                    <td>${u.usuario}</td>

                    <td>${u.nombre_completo}</td>

                    <td>
                        <span class="badge bg-danger">
                            ${u.rol}
                        </span>
                    </td>

                    <td>${u.email || ''}</td>

                    <td>${u.telefono || ''}</td>

                    <td>
                        <span class="badge bg-success">
                            Activo
                        </span>
                    </td>

                    <td>

                        <button 
                            class="btn btn-warning btn-sm"
                            onclick="editarUsuario(${u.id}, '${u.nombre_completo}', '${u.usuario}', '${u.rol}', '${u.email || ''}', '${u.telefono || ''}')"
                        >
                            ✏️
                        </button>

                        <button 
                            class="btn btn-danger btn-sm"
                            onclick="eliminarUsuario(${u.id})"
                        >
                            🗑️
                        </button>

                    </td>

                </tr>
            `;

        });

        document.getElementById('tablaUsuarios')
            .innerHTML = html;

    } catch(err){

        console.error(err);

    }

}


// =====================================
// ELIMINAR USUARIO
// =====================================
async function eliminarUsuario(id){

    if(!confirm('¿Eliminar usuario?')) return;

    try {

        const res = await fetch(`/api/usuarios/${id}`, {

            method: 'DELETE'

        });

        const json = await res.json();

        if(json.success){

            cargarUsuarios();

        }

    } catch(err){

        console.error(err);

    }

}


// =====================================
// CARGAR AUTOMÁTICO
// =====================================
document.getElementById('modalListaUsuarios')
.addEventListener('show.bs.modal', function(){

    cargarUsuarios();

});

// =====================================
// RESETEAR ID AL CERRAR MODAL
// =====================================
document.getElementById('modalUsuario')
.addEventListener('hidden.bs.modal', function(){

    usuarioEditandoId = null;

    document.getElementById('formUsuario').reset();

});