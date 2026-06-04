import { NgIf } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs';

import { AdminSession } from './admin.session';

@Component({
  standalone: true,
  selector: 'app-admin-layout',
  imports: [NgIf, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './admin-layout.component.html',
  styleUrl: './admin-layout.component.scss'
})
export class AdminLayout {
  protected readonly session = inject(AdminSession);
  protected readonly sidebarOpen = signal(false);
  private readonly router = inject(Router);

  constructor() {
    this.router.events.pipe(filter((e) => e instanceof NavigationEnd)).subscribe(() => this.closeSidebar());
  }

  toggleSidebar() {
    this.sidebarOpen.update((v) => !v);
  }

  closeSidebar() {
    this.sidebarOpen.set(false);
  }

  logout() {
    this.session.logout();
    void this.router.navigateByUrl('/admin/login');
  }
}
