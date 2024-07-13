<template>
  <span title="back to root" class="pi pi-home clickable big" @click="backToHome()" />
  <span title="toggle dark mode" class="clickable pi pi-sun big" @click="toggleDark()" />
  <span title="upload some files" class="clickable pi pi-upload big" @click="toggleUpload()" />
  <span class="pi pi-folder-plus clickable big" @click="makeFolder()" title="Create a new folder" />

  <div style="margin: 1em">
    <div v-if="current_path.length" style="font-size: 200%">
      <span title="back one level" class="pi pi-chevron-left clickable" @click="browseBack()" />
      <span v-text="current_path.join('/')" />&nbsp;
      <span title="Download this folder" class="clickable" @click="action_download_current()">
        <span class="pi pi-folder" />&nbsp;
        <span class="pi pi-download" />
      </span>
    </div>

    <FileEntry :items="folders" style="font-weight: bold; color: rgb(100, 150, 250)" />
    <FileEntry :items="files" style="" />

    <Modal id="input_modal" :title="modal_title" :on_validate="accept_modal">
      <template v-slot>
        <input type="text" v-model="modal_text" />
      </template>
    </Modal>

    <dialog id="upload_dialog">
      <article>
        <header>
          <span style="font-size: 200%">File upload</span>
        </header>
        <form
          style="flex-direction: column; display: flex; flex-shrink: 1; align-items: flex-end; justify-content: flex-end">
          <FileUpload style="font-size: 150%" name="files" url="/upload" :maxFileSize="1000000000"
            @upload="action_browse()" customUpload @uploader="customUploader" chooseLabel="&nbsp;Select"
            uploadLabel="&nbsp;Upload" cancelLabel="&nbsp;Cancel" chooseIcon="pi pi-file-arrow-up"
            :showCancelButton="false" :showUploadButton="false" :auto="true" :multiple="true">
            <template #empty>
              <div style="min-height: 100px">Drag and drop files to here to upload.</div>
            </template>
          </FileUpload>

          <button type="submit" aria-label="close" formmethod="dialog" formnovalidate class="secondary">
            <span class="pi pi-times" />
          </button>
        </form>
      </article>
    </dialog>

  </div>
</template>

<style scoped>
article {
  padding-bottom: 0;
}

.clickable {
  cursor: pointer;
  padding: 1ex;

  &:hover {
    border-radius: 3px;
    background-color: rgb(40, 60, 80);
    color: #fff;
    animation-duration: 300ms;
  }
}

.upload_button {
  font-size: 120%;
  margin-right: 1ex;
  padding: .3ex;
}

.big {
  font-size: 200%;
}
</style>

<script setup>
const modal_accepted_event = new Event('modalAccepted');
// emit the event
function accept_modal() {
  document.dispatchEvent(modal_accepted_event);

}
const HOST = import.meta.env.DEV ? "http://localhost:5566" : ''
import { ref, onMounted } from 'vue';
import FileEntry from './FileEntry.vue';
import Modal from './Modal.vue';
import config from '../site_config.js';

import 'primeicons/primeicons.css';

import FileUpload from 'primevue/fileupload';

import { download } from './utils';

const current_path = ref([]);
const files = ref([]);
const folders = ref([])
const modal_text = ref('');
const modal_title = ref('');

let selectedFile = null;

async function customUploader(params) {
  const form = new FormData();

  for (let file of params.files) {
    form.append('files', new File(
      [file],
      get_stripped_path(file.name),
      { type: file.type }
    ));
  }

  fetch(HOST + '/upload', {
    method: 'POST',
    body: form
  }).then(() => {
    action_browse();
  });
}


function get_stripped_path(filename) {
  return current_path.value.length ? current_path.value.join('/') + '/' + filename : filename
}

const action_download_current = () => {
  const path = current_path.value.join('/');
  const fname = current_path.value.join('-')
  download(`download-zip/${path}`, `${fname}.zip`);
};

const action_download_folder = (folder) => {
  const path = get_stripped_path(folder);
  download(`download-zip/${path}`, `${folder}.zip`);
};

const action_download_file = (filename) => {
  const path = get_stripped_path(filename);
  if (config.direct_download_path) {
    download(`${config.direct_download_path}${path}`, filename);

  } else {
    download(`download/${path}`, filename);
  }
}

async function makeFolder() {
  modal_title.value = 'Folder name';
  toggleInputModal();
  const modalAcceptedHandler = async () => {
    if (!modal_text.value) return;
    await fetch(HOST + '/mkdir/' + get_stripped_path(modal_text.value), { method: 'POST' });
    modal_text.value = '';
    await action_browse();
  }
  document.addEventListener('modalAccepted', modalAcceptedHandler, { once: true })
}

const action_browse = async () => {
  const path = current_path.value.length ? current_path.value.join('/') : '';
  const response = await fetch(HOST + '/files/' + path);
  const data = await response.json();
  folders.value = data.folders.map((folder) => {
    return {
      name: folder,
      icon: "pi pi-folder",
      download: action_download_folder,
      action: openFolder,
      action_title: "Open folder",
    };
  });
  files.value = data.files.map((file) => {
    return {
      name: file,
      icon: "pi pi-file",
      download: action_download_file,
      action: () => alert("TODO: play video, view image, edit text..."),
      action_title: "To be implemented",
    };
  });
};

const backToHome = async () => {
  current_path.value = [];
  await action_browse();
};
const openFolder = async (folder) => {
  current_path.value.push(folder);
  await action_browse();
};

const browseBack = async () => {
  await current_path.value.pop();
  await action_browse();
};
function toggleDark() {
  const doc = document.documentElement;
  // doc.dataset.theme = doc.dataset.theme === 'dark' ? 'light' : 'dark';
  const isLight = doc.getAttribute('data-theme') === 'light';
  doc.setAttribute('data-theme', isLight ? 'dark' : 'light');
}

onMounted(action_browse);

function toggleInputModal() {
  const dialog = document.querySelector('#input_modal')
  if (dialog.hasAttribute('open')) {
    dialog.close();
  } else {
    dialog.showModal();
  }
}
function toggleUpload() {
  const dialog = document.querySelector('#upload_dialog')
  if (dialog.hasAttribute('open')) {
    dialog.close();
  } else {
    dialog.showModal();
  }
}
</script>
