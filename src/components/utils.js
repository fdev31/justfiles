function download(path, fileName) {
    const link = document.createElement('a');
    link.href = `/${path}`;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

export { download };
