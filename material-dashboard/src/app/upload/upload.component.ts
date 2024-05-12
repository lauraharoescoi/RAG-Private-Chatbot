import { Component, ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss']
})
export class UploadComponent {
  files: File[] = [];

  constructor(private changeDetector: ChangeDetectorRef) {}

  handleFileInput(files: FileList) {
    Array.from(files).forEach(file => {
      this.files.push(file);
    });
    this.changeDetector.markForCheck();  // Trigger change detection manually
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
  }
}
