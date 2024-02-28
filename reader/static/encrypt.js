async function pwdToKey(username, password) {
    const salt = new Uint8Array(16);
    salt.set(new TextEncoder().encode(username));

    const iterations = 100000;

    try {
        const keyMaterial = await window.crypto.subtle.importKey(
            "raw",
            new TextEncoder().encode(password),
            "PBKDF2",
            false,
            ["deriveBits", "deriveKey"]
        );

        let key = await window.crypto.subtle.deriveKey(
            {
                name: "PBKDF2",
                salt: salt,
                iterations: iterations,
                hash: "SHA-256"
            },
            keyMaterial,
            {name: "AES-GCM", length: 256},
            true,
            ["encrypt", "decrypt"]
        );
        return key;
    } catch (error) {
        console.error("Error generating PBKDF2 key:", error);
        return null;
    }
}
function toHexString(byteArray) {
    return [...new Uint8Array(byteArray)]
      .map(x => x.toString(16).padStart(2, '0'))
      .join('');
}
async function readFileContent(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);

        reader.readAsArrayBuffer(file);
    });
}
async function encryptFile(file, key) {
    const content = await readFileContent(file);
    const iv = window.crypto.getRandomValues(new Uint8Array(16));

    const encryptedContent = await window.crypto.subtle.encrypt(
        { name: "AES-CBC", iv },
        key,
        content
    );

    const filenameBytes = new TextEncoder().encode(file.name);
    const encryptedFilename = await window.crypto.subtle.encrypt(
        { name: "AES-CBC", iv },
        key,
        filenameBytes
    );

    return {
        encrypted: new Uint8Array(encryptedContent),
        filename: new Uint8Array(encryptedFilename),
        iv: new Uint8Array(iv)
    };
}

function hexToByteArray(hexKey) {
  if (hexKey.length % 2 !== 0) {
    throw new Error("Invalid data");
  }

  const byteArray = new Uint8Array(hexKey.length / 2);

  for (let i = 0; i < hexKey.length; i += 2) {
    const byteValue = parseInt(hexKey.substr(i, 2), 16);
    if (isNaN(byteValue)) {
      throw new Error("Invalid data");
    }
    byteArray[i / 2] = byteValue;
  }

  return byteArray;
}

async function decryptUtil(buffer, key, iv) {
    return await window.crypto.subtle.decrypt(
        {
            name: "AES-CBC",
            iv: iv
        },
        key,
        buffer
    );
}
async function decryptFile(filename, content, key, iv) {
    let decryptedFilename = await decryptUtil(filename, key, iv);
    let decryptedContent = await decryptUtil(content, key, iv);
    let blob = new Blob([decryptedContent], { type: 'application/octet-stream'});
    return new File([blob], new TextDecoder().decode(decryptedFilename), { type: 'application/pdf' });
}