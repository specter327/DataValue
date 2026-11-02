#!/bin/bash

# Configuracion específica
PACKAGE_NAME="datavalue";
PYPROJECT_FILE="pyproject.toml";

echo "[*] Iniciando proceso de actualizacion...";

# Eliminacion de residuos de compilaciones previas
echo "[*] Eliminando residuos de compilaciones previas...";
rm -rf dist/ build/ *.egg-info;

echo "[*] Eliinando residuos de ejecuciones previas...";
find . -type d -name "__pycache__" -exec rm -rf {} +;

# Deteccion e incremento de version
if [ -f "$PYPROJECT_FILE" ]; then
    CURRENT_VERSION=$(grep -oP 'version\s*=\s*"\K[^"]+' "$PYPROJECT_FILE")
    echo "[+] Versión actual: $CURRENT_VERSION"
    
    # Lógica de incremento X.Y.Z -> X.Y.Z+1
    NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{$NF = $NF + 1;} OFS="." {print $1, $2, $3}')
    
    sed -i "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" "$PYPROJECT_FILE"
    echo "[+] Nueva versión establecida: $NEW_VERSION"
else
    echo "[!] Error: No se encontró el archivo $PYPROJECT_FILE"
    exit 1
fi

# Compilacion del nuevo paquete
echo "[*] Compilando nueva version del paquete...";
python3 -m build

# Publicacion de la nueva version del paquete en PyPi
echo "[*] Publicando en PyPi...";
if python3 -m twine upload dist/*; then
    echo "[+] Publicación en PyPI exitosa."
else
    echo "[!] Error crítico en la publicacion a PyPI. Abortando proceso"
    exit 1
fi

# 5. Sincronización opcional con el Monorepo en GitHub
echo -n "[?] ¿Deseas actualizar el repositorio en Github? (Y/n): ";
read -r response;

case "$response" in
    [yY][eE][sS]|[yY]|"")
        echo "[*] Iniciando sincronizacion con Github...";
        
        # Validación de pertenencia al árbol de Git (Monorepo)
        if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
            git add .
            git commit -m "DataValue: Actualizacion automatica v$NEW_VERSION";
            git push origin main;
            echo "[*] Sincronizacion de código completada.";

            # 6. Lógica de Tag/Release (Crucial para librerías base)
            echo -n "[?] ¿Es esta una versión oficial? (Esto creara una nueva version en Github) (y/N): ";
            read -r tag_response;

            if [[ "$tag_response" =~ ^[yY]$ ]]; then
                TAG_NAME="datavalue-v$NEW_VERSION"
                echo "[*] Creando etiqueta de versión: $TAG_NAME..."
                git tag -a "$TAG_NAME" -m "Release oficial de DataValue versión $NEW_VERSION"
                git push origin "$TAG_NAME"
                echo "[+] Etiqueta publicada en Github.";
            else
                echo "[*] Actualizacion finalizada sin etiquetas.";
            fi
        else
            echo "[!] Error: No se detectó un repositorio Git.";
        fi
        ;;
    [nN]*)
        echo "[*] Omitiendo sincronización con Github.";
        ;;
esac

echo "[*] Finalizando actualizacion del sistema.";