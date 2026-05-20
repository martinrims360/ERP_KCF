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