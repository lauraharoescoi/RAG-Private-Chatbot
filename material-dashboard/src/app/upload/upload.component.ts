import { Component } from '@angular/core';

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss']
})
export class UploadComponent {
  files: File[] = [];

  handleFileInput(files: FileList) {
    Array.from(files).forEach(file => this.files.push(file));
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    const files = event.dataTransfer?.files;
    if (files) {
      this.handleFileInput(files);
    }
  }

  uploadFiles() {
    console.log('Files to upload:', this.files);
    // Implement your upload logic here
  }

  removeFile(index: number): void {
    this.files.splice(index, 1); // Removes the file from the array
  }
}
