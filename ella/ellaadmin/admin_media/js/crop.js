/* File crop.js
 * Script defines an image crop area
 * Author: Izmaylov Maxim (izmaylov.maxim@netcentrum.cz)
 * Copyright: NetCentrum @2007
 * Requirements: jquery.js, interface resizeables (interface.js)
 */
function annihilateCropper(){
	if(!arguments[0].keyCode || arguments[0].keyCode == 27){
		$('#wrapper, #cropper, #cropContainer').remove();
		$('#cropper').ResizableDestroy();
		window.location.href = '#' + itemId;
	}
}

function buildCropper(row, itemId){
	var formatId = row.find('select').val();
	if(formatId){
		$.getJSON(formatId + '/json/', function(data){
			if(!data.error){
				image = {
					url : data.image,
					width : data.width,
					height : data.height
				};
				format = {
					width : data.format_width,
					height : data.format_height
				};
				cLeft = $(row.find('.crop_left input')[0]);
				cTop = $(row.find('.crop_top input')[0]);
				cWidth = $(row.find('.crop_width input')[0]);
				cHeight = $(row.find('.crop_height input')[0]);
				mh = (document.documentElement.scrollHeight || document.body.scrollHeight);
				mw = (document.documentElement.scrollWidth || document.body.scrollWidth);
				lb = Math.round((mw - image.width) / 2);
				$('body').append(
					$('<div id="wrapper"></div>').css({
						height: mh + 'px',
						opacity: 0
					}).animate({ opacity: 0.75 }, 'slow'),
					$('<div id="cropContainer"></div>').
						css({
							width: image.width + 'px',
							height: image.height + 'px',
							left: lb + 'px',
							background: 'url(' + image.url + ') left top no-repeat'
						}),
					$('<div id="cropper"><div id="resizeSE"></div></div>').
						css({
							width: (cWidth.val() - 0) + 'px',
							height: (cHeight.val() - 0) + 'px',
							left: lb + (cLeft.val() - 0) + 'px',
							top: 50 + (cTop.val() - 0) + 'px',
							background: 'url(' + image.url + ') left top no-repeat',
							backgroundPosition: '-' + (cLeft.val() - 0) + 'px -' + (cTop.val() - 0) + 'px'
						})
				);
				$('#cropper').Resizable({
					minWidth: 20,
					minHeight: 20,
					maxWidth: image.width,
					maxHeight: image.height,
					minTop: 50,
					minLeft: lb,
					maxRight: lb + image.width,
					maxBottom: 50 + image.height,
					dragHandle: true,
					ratio: format.height / format.width,
					onDrag: function(x, y){
						this.style.backgroundPosition = '-' + (x - lb) + 'px -' + (y - 50) + 'px';
						cLeft.val(x - lb);
						cTop.val(y - 50);
					},
					handlers: {
						se: '#resizeSE'
					},
					onResize: function(size, position){
						this.style.backgroundPosition = '-' + (position.left - lb) + 'px -' + (position.top - 50) + 'px';
						cWidth.val(Math.round(size.width));
						cHeight.val(Math.round(size.height));
					}
				});
				$(document).bind('keyup', annihilateCropper);
			}
		});
	} else {
		alert('Error: unexpected order of elements.');
	}
}

$(function(){
	$('.has_original').each(function(i){
		$(this).find('td.original p').wrapInner('<a href="#cropper" id="photo-' + i + '"></a>').click(function(event){
			event.preventDefault();
			itemId = 'photo-' + i;
			buildCropper($(this).parent().parent());
			window.setTimeout(function(){
				location.href = '#wrapper';
			}, 500);
		});
		$(this).find('td.format select').attr('disabled', 'disabled');
		$(this).find('td.format a').remove();
	});
});