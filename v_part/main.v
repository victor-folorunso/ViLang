<#
multi line comment
#>
# single line comment


include lib
from folder.subfolder include file

_scree = {
  color: red,
  draw_hide:draw,
  shape: square,
  height: 128,
  width: 72,
  position_xy: [20,20],
}    

greet_user(){
  <#
    greet_user
  #>
}

change_color(){
  _nilo.color: green
  _scree = {
    color: red,
    draw_hide: draw,
  }
}

containers = [_container1,_scree]  
    
main _screen = {                         
  color: green,              
  draw_hide: draw,         
  shape: circle,
  height: 1280,
  width: 720,
  position_xy: [20,20],
  children: [
    _nilo = {
      color: blue,
      draw_hide: hide,
      shape: square,
      height: 128,
      width: 72,
      children: containers,
    },
    _scree,
  ],
  event_listner: { 
    on_click: greet_user(),
    on_long_press: [
      greet_uqser(),
      change_color(),
    ],
  },
}