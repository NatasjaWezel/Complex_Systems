import { Component, OnInit, HostListener } from '@angular/core';

@Component({
  selector: 'app-results-page',
  templateUrl: './results-page.component.html',
  styleUrls: ['./results-page.component.css', '../shared.css']
})
export class ResultsPageComponent implements OnInit {

  hidden = true;

  constructor() { }

  ngOnInit() {
  }

  @HostListener('document:keydown', ['$event'])
  handleKeyboardEvent(event: KeyboardEvent) {
    const key = event.key;
    if (key === 'enter') {
      this.hidden = false;
    }
  }

}
