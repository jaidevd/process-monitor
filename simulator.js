/* globals g1 */

const EDIT_OPTS = {
  'material-a':
    '<select id="material-a" class="form-control svgin"><option value="A1">A1</option><option value="A2">A2</option></select>',
  'material-b': '<select id="material-b" class="form-control svgin"><option value="B1">B1</option><option value="B2">B2</option></select>',
  solvent: '<select id="solvent" class="form-control svgin"><option value="Low">Low</option><option value="Hi">Hi</option></select>',
  reactor: '<input id="reactor-speed" type="range" min="80" max="86" value="83" step="1"  class="form-control svgin">',
  dryer: '<input id="dryer-speed" type="range" min="20" max="25" value="22" step="1"  class="form-control svgin">',
  crusher: '<input id="crusher-speed" type="range" min="12" max="15" value="14" step="1"  class="form-control svgin">',
  crystallizer: '<input id="crystallizer-speed" type="range" min="10" max="15" value="12" step="1"  class="form-control svgin">'
}

$(function () {
  var $template = $('script[type="text/html"]')
  var url = g1.url.parse(location.href)
  var simulate = url.pathname.includes('/simulator')
  var q = url.searchKey
  var duration = +(q.duration || 120)

  var charts = {
    area: function ({ data, index, x, y, width = 180, height = 80, fill = 'steelblue', margin = { left: 0, right: 0, bottom: 0, top: 0 } }) {
      data = data.slice(Math.max(0, index - duration), index)
      fill = Array.isArray(y) ? fill : [fill]
      y = Array.isArray(y) ? y : [y]
      var scales = {
        x: d3.scaleLinear()
          .domain(d3.extent(data, d => d[x]))
          .range([margin.left, width - margin.right]),
        y: d3.scaleLinear()
          .domain([0, d3.max(y.map(_y => d3.max(data, d => d[_y])))]).nice()
          .range([height - margin.bottom, margin.top])
      }
      var path = ''
      y.forEach((y_, i) => {
        var p1 = d3.area()
          .defined(d => !isNaN(d[y_]))
          .x(d => scales.x(d[x]))
          .y0(scales.y(0))
          .y1(d => scales.y(d[y_]))(data)
        var p2 = d3.line()
          .defined(d => !isNaN(d[y_]))
          .x(d => scales.x(d[x]))
          .y(d => scales.y(d[y_]))(data)
        if (p1.includes('NaN')) return
        path += `<path d="${p1}" fill="${fill[i]}" fill-opacity="0.1" />
        <path d="${p2}" fill="none" stroke="${fill[i]}" stroke-width="2" />`
      })
      return path
    }
  }
  function render_popover_content() {
    let html = EDIT_OPTS[this.className.baseVal]
    return html
  }

  function render_popover_title() {
    let param = $(this).attr('data-param')
    return "Change " + param
  }

  if ($template.length)
    $.getJSON($template.data('src') || 'data').done(function (data) {
      $('.loading').remove()
      var index = q.time ? +q.time - 1 : 0
      render()
      $('[data-toggle="popover"]').on('shown.bs.popover', function(evt) {
        $('.svgin').change(function() {
          let param_id = $(this).attr('id')
          if (param_id == "solvent") {
            $('#solvent-' + $(this).val().toLowerCase()).attr('checked', true)
          } else {
            $(`form #${param_id}`).val($(this).val())
          }
          $('.controls').change()
        })
      }).popover({
        html: true,
        sanitize: false,
        title: render_popover_title,
        content: render_popover_content
      })
      function render() {
        $template.template({ row: data[index++], data: data, simulate, index, charts })
        if (index < data.length)
          setTimeout(render, 1000 / (q.speed || 10))
      }
    })

  $('.controls').on('change', function () {
    $('form').submit()
  }).on('input', 'input', function () {
    $('#' + $(this).attr('name')).html(this.value + '%')
  })
})
