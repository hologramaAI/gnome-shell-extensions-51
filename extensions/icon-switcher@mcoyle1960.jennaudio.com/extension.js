// extension.js
//
//		Icon Switcher - GNOME Shell Extension by Michael Coyle
//		Quick-access menu to switch between installed icon themes and accent colors.
//		v3. Updated from Gnome 50 and slight code cleanup.

import GObject from 'gi://GObject';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import St from 'gi://St';

import {Extension, gettext as _} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

const INTERFACE_SETTINGS = 'org.gnome.desktop.interface';
const ICON_KEY = 'icon-theme';
const ACCENT_KEY = 'accent-color';
const ACCENT_COLORS = 
	[
		'blue', 'teal', 'green', 'yellow', 'orange', 'red', 'pink', 'purple', 'slate'
	];


 //Scans standard directories for valid icon themes with an index file. 
function getAvailableIconThemes() 
{
	const themes = new Set();
	const paths = 
	[
		GLib.build_filenamev([GLib.get_home_dir(), '.local', 'share', 'icons']),
		'/usr/share/icons'
	];

	for (const path of paths) 
	{
		const dir = Gio.File.new_for_path(path);
		try 
		{
			const enumerator = dir.enumerate_children
			(
				'standard::name,standard::type',
				Gio.FileQueryInfoFlags.NONE,
				null
			);

			let info;
			let count = 0;
			while ((info = enumerator.next_file(null)) && count++ < 500) 
			{
				if (info.get_file_type() !== Gio.FileType.DIRECTORY)
					continue;

				const name = info.get_name();
				const indexFile = dir.get_child(name).get_child('index.theme');
                
				if (indexFile.query_exists(null))
					themes.add(name);
			}
			enumerator.close(null);
		} catch (e) {
			// Path missing or inaccessible
		}
	}
	return [...themes].sort((a, b) => a.localeCompare(b));
}

// Defines the panel button and its menu.
const Indicator = GObject.registerClass(
{
	GTypeName: 'IconSwitcherIndicator',
}, 

class Indicator extends PanelMenu.Button 
{
	_init() 
	{
		super._init(0.0, _('Icon Theme Switcher'));
		this.accessible_name = _('Icon Theme Switcher');
		this._iconMenuItems = {}; 
		this._accentMenuItems = {}; 

		this._interfaceSettings = new Gio.Settings(
		{
			schema_id: INTERFACE_SETTINGS 
		});

		// Check is any other app has changed the settings.
		this._interfaceSettings.connectObject(
			`changed::${ICON_KEY}`, () => this._updateMenuIndicators(),
			`changed::${ACCENT_KEY}`, () => this._updateMenuIndicators(),
		this
		);
		
		this.add_child(new St.Icon(
		{
			icon_name: 'preferences-desktop-theme-symbolic',
			style_class: 'system-status-icon',
		}));
		this._buildMenu();
	}  
		//  Let's build us a menu!'
		_buildMenu() 
		{
			this.menu.removeAll();
			this._iconMenuItems = {};
			this._accentMenuItems = {};

			//  Icon theme menu
			this._iconSubMenu = new PopupMenu.PopupSubMenuMenuItem(_('Select Icon Theme'), true);
			this._iconSubMenu.icon.icon_name = 'preferences-desktop-theme-symbolic';
			this.menu.addMenuItem(this._iconSubMenu);
        
			// Icon theme submenu
			const refreshItem = new PopupMenu.PopupImageMenuItem(_('Refresh List'), 'view-refresh-symbolic');
			refreshItem.connect('activate', () => this._buildMenu());
			this._iconSubMenu.menu.addMenuItem(refreshItem);
			this._iconSubMenu.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        
			// Set NONE to reserve space for the radio-button column. Kinda works
			const themes = getAvailableIconThemes();
			const currentTheme = this._interfaceSettings.get_string(ICON_KEY);
				themes.forEach(themeName => 
				{
					const item = new PopupMenu.PopupMenuItem(themeName);
					this._iconMenuItems[themeName] = item;
					item.setOrnament(themeName === currentTheme 
					? PopupMenu.Ornament.DOT 
					: PopupMenu.Ornament.NONE);

					item.connect('activate', () => this._interfaceSettings.set_string(ICON_KEY, themeName));
					this._iconSubMenu.menu.addMenuItem(item);
				});        

			// Accent Color menu
			this._accentSubMenu = new PopupMenu.PopupSubMenuMenuItem(_('Select Accent Color'), true);
			this._accentSubMenu.icon.icon_name = 'preferences-desktop-appearance-symbolic';
			this.menu.addMenuItem(this._accentSubMenu);

			// Accent Color submenu
			const currentAccent = this._interfaceSettings.get_string(ACCENT_KEY);
			ACCENT_COLORS.forEach(color => 
				{
					const label = color.charAt(0).toUpperCase() + color.slice(1);
					const item = new PopupMenu.PopupMenuItem(_(label));
					this._accentMenuItems[color] = item;
            
					// Set NONE to reserve space for the radio-button column. Kinda works
					item.setOrnament(color === currentAccent 
					? PopupMenu.Ornament.DOT 
					: PopupMenu.Ornament.NONE);
					item.connect('activate', () => this._interfaceSettings.set_string(ACCENT_KEY, color));
					this._accentSubMenu.menu.addMenuItem(item);
				});
		}     

		_updateMenuIndicators()
		{
			const currentTheme = this._interfaceSettings.get_string(ICON_KEY);
			const currentAccent = this._interfaceSettings.get_string(ACCENT_KEY);

			// Sync Icon Theme dots
			Object.entries(this._iconMenuItems).forEach(([name, item]) => 
			{
				item.setOrnament(name === currentTheme 
				? PopupMenu.Ornament.DOT 
				: PopupMenu.Ornament.NONE);
			});

			// Sync Accent Color dots
			Object.entries(this._accentMenuItems).forEach(([color, item]) =>
			{
				item.setOrnament(color === currentAccent 
				? PopupMenu.Ornament.DOT 
				: PopupMenu.Ornament.NONE);
			});
		}
    
		destroy()
			{
				this._interfaceSettings.disconnectObject(this);
				super.destroy();
			}
});

// Hello and Goodbye
export default class IconSwitcherExtension extends Extension 
{
	enable() 
	{
		this._indicator = new Indicator();
		Main.panel.addToStatusArea(this.uuid, this._indicator);
	}

	disable() 
	{
		this._indicator?.destroy();
		this._indicator = null;
	}
}
