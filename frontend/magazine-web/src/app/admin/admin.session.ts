import { Injectable, signal } from '@angular/core';

const LS_KEY = 'mn_admin_key';
const LS_TOKEN = 'mn_admin_token';

@Injectable({ providedIn: 'root' })
export class AdminSession {
  private readonly _loggedIn = signal<boolean>(!!localStorage.getItem(LS_TOKEN));

  loggedIn() {
    return this._loggedIn();
  }

  getKey(): string | null {
    return localStorage.getItem(LS_KEY);
  }

  getToken(): string | null {
    return localStorage.getItem(LS_TOKEN);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  login(adminKey: string) {
    localStorage.setItem(LS_KEY, adminKey);
  }

  loginWithToken(token: string) {
    localStorage.setItem(LS_TOKEN, token);
    this._loggedIn.set(true);
  }

  logout() {
    localStorage.removeItem(LS_KEY);
    localStorage.removeItem(LS_TOKEN);
    this._loggedIn.set(false);
  }
}

