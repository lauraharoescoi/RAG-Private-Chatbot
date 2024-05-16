// upload.component.ts
import { Component } from '@angular/core';
import { HttpEventType } from '@angular/common/http';
import { ConversationService } from '../services/conversation.service';
import { FilesService } from '../services/files.service';
import { MatSnackBar } from '@angular/material/snack-bar';  
import { NotificationService } from '../services/notifications.service'; // Import the new service

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss']
})
export class UploadComponent {
  files: File[] = [];
  uploading: boolean = false;

  constructor(private conversationService: ConversationService, 
              private snackBar: MatSnackBar, 
              private notificationService: NotificationService,
              private filesService: FilesService) {}

  handleFileInput(files: FileList) {
    Array.from(files).forEach(file => {
      if (file.type === "application/pdf") {
        this.files.push(file);
      } else {
        this.snackBar.open('Only PDF files are allowed!', 'Close', { duration: 3000 });
      }
    });
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
    this.uploading = true;
    const uploadRequests = this.files.map(file => this.uploadFile(file));
    Promise.all(uploadRequests)
      .then(() => {
        this.uploading = false;
        this.files = []; // Clear the files array after all uploads are complete
      })
      .catch(error => {
        console.error('Upload failed:', error);
        this.uploading = false;
      });
  }
  
  uploadFile(file: File): Promise<void> {
    return new Promise<void>((resolve, reject) => {
      this.filesService.uploadFile(file).subscribe(event => {
        if (event.type === HttpEventType.Response) {
          this.notificationService.showNotification('top', 'right', `File '${file.name}' uploaded successfully.`, 'success');
          const index = this.files.indexOf(file);
          if (index !== -1) {
            this.files.splice(index, 1);
          }
          resolve(); // No es necesario pasar ningún argumento a resolve()
        }
      }, error => {
        console.error('Upload failed:', error);
        reject(error); // Reject the promise on upload failure
      });
    });
  }
   

  removeFile(index: number): void {
    if (!this.uploading) {
      this.files.splice(index, 1);
    }
  }
}
