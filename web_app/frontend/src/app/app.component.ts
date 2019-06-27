import { Component, ViewChild, ElementRef, OnInit, AfterViewInit } from '@angular/core';
import { HostListener } from '@angular/core';
import { ApiService } from 'src/services/api.service';
import { LandingComponent } from './landing/landing.component';
import { TheoryPageComponent } from './theory-page/theory-page.component';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, AfterViewInit {

  @ViewChild('landing', {read: ElementRef}) lan: ElementRef;
  @ViewChild('first', {read: ElementRef}) f: ElementRef;
  @ViewChild('second', {read: ElementRef}) s: ElementRef;
  @ViewChild('theory', {read: ElementRef}) t: ElementRef;
  @ViewChild('third', {read: ElementRef}) third: ElementRef;
  @ViewChild('fourth', {read: ElementRef}) fourth: ElementRef;
  @ViewChild('model', {read: ElementRef}) model: ElementRef;
  @ViewChild('simulations', {read: ElementRef}) sim: ElementRef;
  @ViewChild('results', {read: ElementRef}) res: ElementRef;
  @ViewChild('discussion', {read: ElementRef}) dis: ElementRef;



  elements: ElementRef[];

  active: number;

  constructor(private _api: ApiService) {

  }

  ngOnInit() {
    this.active = 0;
  }

  ngAfterViewInit() {
    this.elements = [this.lan, this.f, this.s, this.t, this.third, this.fourth, this.model, this.sim, this.res, this.dis];
  }

  @HostListener('document:keydown', ['$event'])
  handleKeyboardEvent(event: KeyboardEvent) {
    const key = event.key;
    if (key === 'ArrowRight') {
      this.active += 1;
      this.scroll();
    } else if (key === 'ArrowLeft') {
      this.active -= 1;
      this.scroll();
    }
  }

  scroll() {
    if (this.active < 0) {
      this.active = 0;
    } else if (this.active > 9) {
      this.active = 9;
    }
    this.elements[this.active].nativeElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

}
