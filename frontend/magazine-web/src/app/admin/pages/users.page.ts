import { DatePipe, NgFor, NgIf } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AdminApi, AdminUser } from '../admin.api';
import { AdminSession } from '../admin.session';

@Component({
  standalone: true,
  selector: 'app-admin-users',
  imports: [NgFor, NgIf, DatePipe, FormsModule],
  templateUrl: './users.page.html',
  styleUrls: ['../admin.shared.scss', './users.page.scss']
})
export class AdminUsersPage implements OnInit {
  private readonly api = inject(AdminApi);
  private readonly session = inject(AdminSession);

  loading = true;
  saving = false;
  error = '';
  success = '';
  users: AdminUser[] = [];
  username = '';
  password = '';

  ngOnInit() {
    this.load();
  }

  load() {
    const token = this.session.getToken();
    if (!token) {
      this.loading = false;
      this.error = 'Login required.';
      return;
    }
    this.loading = true;
    this.api.listUsers(token).subscribe({
      next: (rows) => {
        this.users = rows;
        this.loading = false;
      },
      error: () => {
        this.error = 'Users load nahi ho paye.';
        this.loading = false;
      }
    });
  }

  create() {
    const token = this.session.getToken();
    if (!token || !this.username.trim() || !this.password.trim()) return;

    this.saving = true;
    this.error = '';
    this.success = '';

    this.api.createUser({ username: this.username.trim(), password: this.password }, token).subscribe({
      next: () => {
        this.success = 'User created.';
        this.username = '';
        this.password = '';
        this.saving = false;
        this.load();
      },
      error: (err) => {
        this.error = err?.error?.detail ?? 'Create failed.';
        this.saving = false;
      }
    });
  }

  remove(user: AdminUser) {
    if (user.is_builtin) return;
    if (!confirm(`Delete user "${user.username}"?`)) return;
    const token = this.session.getToken();
    if (!token) return;

    this.api.deleteUser(user.id, token).subscribe({
      next: () => this.load(),
      error: (err) => {
        this.error = err?.error?.detail ?? 'Delete failed.';
      }
    });
  }
}
