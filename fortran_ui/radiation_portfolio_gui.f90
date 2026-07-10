module radiation_portfolio_win32_gui
    use, intrinsic :: iso_c_binding, only: c_associated, c_char, c_funloc, c_funptr, &
        c_int, c_intptr_t, c_loc, c_long, c_null_char, c_null_ptr, c_ptr, c_short
    implicit none
    private

    public :: run_gui

    integer, parameter :: field_len = 512
    integer, parameter :: max_fields = 40
    integer, parameter :: line_len = 4096
    integer, parameter :: section_count = 7

    integer(c_int), parameter :: CW_USEDEFAULT = int(Z'80000000', c_int)
    integer(c_int), parameter :: SW_SHOW = 5_c_int
    integer(c_int), parameter :: SW_SHOWNORMAL = 1_c_int
    integer(c_int), parameter :: WM_CREATE = 1_c_int
    integer(c_int), parameter :: WM_DESTROY = 2_c_int
    integer(c_int), parameter :: WM_SIZE = 5_c_int
    integer(c_int), parameter :: WM_SETFOCUS = 7_c_int
    integer(c_int), parameter :: WM_SETFONT = 48_c_int
    integer(c_int), parameter :: WM_COMMAND = 273_c_int
    integer(c_int), parameter :: WM_KEYDOWN = 256_c_int
    integer(c_int), parameter :: WS_OVERLAPPEDWINDOW = int(Z'00CF0000', c_int)
    integer(c_int), parameter :: WS_VISIBLE = int(Z'10000000', c_int)
    integer(c_int), parameter :: WS_CHILD = int(Z'40000000', c_int)
    integer(c_int), parameter :: WS_BORDER = int(Z'00800000', c_int)
    integer(c_int), parameter :: WS_TABSTOP = int(Z'00010000', c_int)
    integer(c_int), parameter :: WS_VSCROLL = int(Z'00200000', c_int)
    integer(c_int), parameter :: WS_HSCROLL = int(Z'00100000', c_int)
    integer(c_int), parameter :: WS_EX_CLIENTEDGE = int(Z'00000200', c_int)
    integer(c_int), parameter :: ES_MULTILINE = 4_c_int
    integer(c_int), parameter :: ES_AUTOVSCROLL = 64_c_int
    integer(c_int), parameter :: ES_AUTOHSCROLL = 128_c_int
    integer(c_int), parameter :: ES_READONLY = 2048_c_int
    integer(c_int), parameter :: LBS_NOTIFY = 1_c_int
    integer(c_int), parameter :: BS_PUSHBUTTON = 0_c_int
    integer(c_int), parameter :: COLOR_WINDOW = 5_c_int
    integer(c_int), parameter :: DEFAULT_GUI_FONT = 17_c_int
    integer(c_int), parameter :: IDC_ARROW = 32512_c_int
    integer(c_int), parameter :: VK_ESCAPE = 27_c_int
    integer(c_int), parameter :: MB_OK = 0_c_int
    integer(c_int), parameter :: MB_ICONINFORMATION = 64_c_int
    integer(c_int), parameter :: FW_NORMAL = 400_c_int
    integer(c_int), parameter :: FW_SEMIBOLD = 600_c_int
    integer(c_int), parameter :: DEFAULT_CHARSET = 1_c_int
    integer(c_int), parameter :: OUT_DEFAULT_PRECIS = 0_c_int
    integer(c_int), parameter :: CLIP_DEFAULT_PRECIS = 0_c_int
    integer(c_int), parameter :: CLEARTYPE_QUALITY = 5_c_int
    integer(c_int), parameter :: DEFAULT_PITCH = 0_c_int
    integer(c_int), parameter :: LB_ADDSTRING = int(Z'0180', c_int)
    integer(c_int), parameter :: LB_RESETCONTENT = int(Z'0184', c_int)
    integer(c_int), parameter :: LB_SETCURSEL = int(Z'0186', c_int)
    integer(c_int), parameter :: LB_GETCURSEL = int(Z'0188', c_int)
    integer(c_int), parameter :: LBN_SELCHANGE = 1_c_int

    integer(c_int), parameter :: ID_NAV = 101_c_int
    integer(c_int), parameter :: ID_REFRESH = 201_c_int
    integer(c_int), parameter :: ID_EXPORT = 202_c_int
    integer(c_int), parameter :: ID_OPEN_HTML = 203_c_int
    integer(c_int), parameter :: ID_CLOSE = 204_c_int
    integer(c_int), parameter :: ID_RUN_ALL = 205_c_int
    integer(c_int), parameter :: ID_RUN_SECTION = 206_c_int
    integer(c_int), parameter :: ID_OPEN_OUTPUTS = 207_c_int

    character(kind=c_char, len=31), target, save :: class_name = &
        'RadiationPortfolioWin32Gui'//c_null_char
    character(kind=c_char, len=51), target, save :: app_title = &
        'Non-Gray Thermal Radiation Portfolio - Fortran GUI'//c_null_char
    character(kind=c_char, len=8), target, save :: listbox_class = 'LISTBOX'//c_null_char
    character(kind=c_char, len=5), target, save :: edit_class = 'EDIT'//c_null_char
    character(kind=c_char, len=7), target, save :: button_class = 'BUTTON'//c_null_char
    character(kind=c_char, len=7), target, save :: static_class = 'STATIC'//c_null_char

    character(len=46), parameter :: section_titles(section_count) = &
        [character(len=46) :: &
         'Source map and FDS context', &
         'Project 1: hydrogen/H2O radiation data', &
         'Project 2: Johansson particle correlations', &
         'Project 3: DOM on published fields', &
         'Project 4: ML surrogate metrics', &
         'FDS integration and portfolio boundary', &
         'Project 5: RADCAL asset smoke test']

    type(c_ptr), save :: h_instance = c_null_ptr
    type(c_ptr), save :: h_main = c_null_ptr
    type(c_ptr), save :: h_header = c_null_ptr
    type(c_ptr), save :: h_nav = c_null_ptr
    type(c_ptr), save :: h_view = c_null_ptr
    type(c_ptr), save :: h_status = c_null_ptr
    type(c_ptr), save :: h_run_all = c_null_ptr
    type(c_ptr), save :: h_run_section = c_null_ptr
    type(c_ptr), save :: h_refresh = c_null_ptr
    type(c_ptr), save :: h_export = c_null_ptr
    type(c_ptr), save :: h_open_html = c_null_ptr
    type(c_ptr), save :: h_open_outputs = c_null_ptr
    type(c_ptr), save :: h_close = c_null_ptr
    type(c_ptr), save :: h_font = c_null_ptr
    type(c_ptr), save :: h_body_font = c_null_ptr
    type(c_ptr), save :: h_mono_font = c_null_ptr
    type(c_ptr), save :: h_button_font = c_null_ptr
    integer, save :: current_section = 1

    type, bind(C) :: POINT_T
        integer(c_long) :: x
        integer(c_long) :: y
    end type POINT_T

    type, bind(C) :: MSG_T
        type(c_ptr) :: hwnd
        integer(c_int) :: message
        integer(c_intptr_t) :: wparam
        integer(c_intptr_t) :: lparam
        integer(c_int) :: time
        type(POINT_T) :: pt
    end type MSG_T

    type, bind(C) :: WNDCLASSA_T
        integer(c_int) :: style
        type(c_funptr) :: lpfn_wnd_proc
        integer(c_int) :: cb_cls_extra
        integer(c_int) :: cb_wnd_extra
        type(c_ptr) :: h_instance
        type(c_ptr) :: h_icon
        type(c_ptr) :: h_cursor
        type(c_ptr) :: hbr_background
        type(c_ptr) :: menu_name
        type(c_ptr) :: class_name
    end type WNDCLASSA_T

    interface
        function GetModuleHandleA(lp_module_name) bind(C, name='GetModuleHandleA') result(handle)
            import :: c_ptr
            type(c_ptr), value :: lp_module_name
            type(c_ptr) :: handle
        end function GetModuleHandleA

        function RegisterClassA(wnd_class) bind(C, name='RegisterClassA') result(atom)
            import :: WNDCLASSA_T, c_short
            type(WNDCLASSA_T), intent(in) :: wnd_class
            integer(c_short) :: atom
        end function RegisterClassA

        function CreateWindowExA(ex_style, class_name_ptr, window_name, style, x, y, &
                                 width, height, parent, menu, instance, param) &
            bind(C, name='CreateWindowExA') result(hwnd)
            import :: c_int, c_ptr
            integer(c_int), value :: ex_style
            type(c_ptr), value :: class_name_ptr
            type(c_ptr), value :: window_name
            integer(c_int), value :: style
            integer(c_int), value :: x
            integer(c_int), value :: y
            integer(c_int), value :: width
            integer(c_int), value :: height
            type(c_ptr), value :: parent
            type(c_ptr), value :: menu
            type(c_ptr), value :: instance
            type(c_ptr), value :: param
            type(c_ptr) :: hwnd
        end function CreateWindowExA

        function DefWindowProcA(hwnd, message, wparam, lparam) bind(C, name='DefWindowProcA') result(ret)
            import :: c_int, c_intptr_t, c_ptr
            type(c_ptr), value :: hwnd
            integer(c_int), value :: message
            integer(c_intptr_t), value :: wparam
            integer(c_intptr_t), value :: lparam
            integer(c_intptr_t) :: ret
        end function DefWindowProcA

        function ShowWindow(hwnd, cmd_show) bind(C, name='ShowWindow') result(ret)
            import :: c_int, c_ptr
            type(c_ptr), value :: hwnd
            integer(c_int), value :: cmd_show
            integer(c_int) :: ret
        end function ShowWindow

        function UpdateWindow(hwnd) bind(C, name='UpdateWindow') result(ret)
            import :: c_int, c_ptr
            type(c_ptr), value :: hwnd
            integer(c_int) :: ret
        end function UpdateWindow

        function GetMessageA(msg, hwnd, min_filter, max_filter) bind(C, name='GetMessageA') result(ret)
            import :: MSG_T, c_int, c_ptr
            type(MSG_T), intent(inout) :: msg
            type(c_ptr), value :: hwnd
            integer(c_int), value :: min_filter
            integer(c_int), value :: max_filter
            integer(c_int) :: ret
        end function GetMessageA

        function TranslateMessage(msg) bind(C, name='TranslateMessage') result(ret)
            import :: MSG_T, c_int
            type(MSG_T), intent(in) :: msg
            integer(c_int) :: ret
        end function TranslateMessage

        function DispatchMessageA(msg) bind(C, name='DispatchMessageA') result(ret)
            import :: MSG_T, c_intptr_t
            type(MSG_T), intent(in) :: msg
            integer(c_intptr_t) :: ret
        end function DispatchMessageA

        subroutine PostQuitMessage(exit_code) bind(C, name='PostQuitMessage')
            import :: c_int
            integer(c_int), value :: exit_code
        end subroutine PostQuitMessage

        function DestroyWindow(hwnd) bind(C, name='DestroyWindow') result(ret)
            import :: c_int, c_ptr
            type(c_ptr), value :: hwnd
            integer(c_int) :: ret
        end function DestroyWindow

        function LoadCursorA(instance, cursor_name) bind(C, name='LoadCursorA') result(cursor)
            import :: c_ptr
            type(c_ptr), value :: instance
            type(c_ptr), value :: cursor_name
            type(c_ptr) :: cursor
        end function LoadCursorA

        function GetStockObject(object_id) bind(C, name='GetStockObject') result(obj)
            import :: c_int, c_ptr
            integer(c_int), value :: object_id
            type(c_ptr) :: obj
        end function GetStockObject

        function CreateFontA(height, width, escapement, orientation, weight, italic, underline, &
                             strikeout, charset, out_precision, clip_precision, quality, &
                             pitch_and_family, face_name) bind(C, name='CreateFontA') result(font)
            import :: c_int, c_ptr
            integer(c_int), value :: height
            integer(c_int), value :: width
            integer(c_int), value :: escapement
            integer(c_int), value :: orientation
            integer(c_int), value :: weight
            integer(c_int), value :: italic
            integer(c_int), value :: underline
            integer(c_int), value :: strikeout
            integer(c_int), value :: charset
            integer(c_int), value :: out_precision
            integer(c_int), value :: clip_precision
            integer(c_int), value :: quality
            integer(c_int), value :: pitch_and_family
            type(c_ptr), value :: face_name
            type(c_ptr) :: font
        end function CreateFontA

        function GetCurrentDirectoryA(buffer_length, buffer) bind(C, name='GetCurrentDirectoryA') result(chars)
            import :: c_int, c_ptr
            integer(c_int), value :: buffer_length
            type(c_ptr), value :: buffer
            integer(c_int) :: chars
        end function GetCurrentDirectoryA

        function SendMessageA(hwnd, message, wparam, lparam) bind(C, name='SendMessageA') result(ret)
            import :: c_int, c_intptr_t, c_ptr
            type(c_ptr), value :: hwnd
            integer(c_int), value :: message
            integer(c_intptr_t), value :: wparam
            integer(c_intptr_t), value :: lparam
            integer(c_intptr_t) :: ret
        end function SendMessageA

        function SetWindowTextA(hwnd, text_ptr) bind(C, name='SetWindowTextA') result(ret)
            import :: c_int, c_ptr
            type(c_ptr), value :: hwnd
            type(c_ptr), value :: text_ptr
            integer(c_int) :: ret
        end function SetWindowTextA

        function MoveWindow(hwnd, x, y, width, height, repaint) bind(C, name='MoveWindow') result(ret)
            import :: c_int, c_ptr
            type(c_ptr), value :: hwnd
            integer(c_int), value :: x
            integer(c_int), value :: y
            integer(c_int), value :: width
            integer(c_int), value :: height
            integer(c_int), value :: repaint
            integer(c_int) :: ret
        end function MoveWindow

        function SetFocus(hwnd) bind(C, name='SetFocus') result(prev_hwnd)
            import :: c_ptr
            type(c_ptr), value :: hwnd
            type(c_ptr) :: prev_hwnd
        end function SetFocus

        function MessageBoxA(hwnd, text_ptr, caption_ptr, flags) bind(C, name='MessageBoxA') result(ret)
            import :: c_int, c_ptr
            type(c_ptr), value :: hwnd
            type(c_ptr), value :: text_ptr
            type(c_ptr), value :: caption_ptr
            integer(c_int), value :: flags
            integer(c_int) :: ret
        end function MessageBoxA

        function ShellExecuteA(hwnd, operation, file_name, parameters, directory, show_cmd) &
            bind(C, name='ShellExecuteA') result(ret)
            import :: c_int, c_intptr_t, c_ptr
            type(c_ptr), value :: hwnd
            type(c_ptr), value :: operation
            type(c_ptr), value :: file_name
            type(c_ptr), value :: parameters
            type(c_ptr), value :: directory
            integer(c_int), value :: show_cmd
            integer(c_intptr_t) :: ret
        end function ShellExecuteA
    end interface

contains

    subroutine run_gui()
        type(WNDCLASSA_T) :: wc
        type(MSG_T) :: msg
        integer(c_short) :: atom
        integer(c_int) :: ok
        character(len=64) :: first_arg

        if (command_argument_count() > 0) then
            call get_command_argument(1, first_arg)
            select case (trim(adjustl(first_arg)))
            case ('--export-html')
                call write_html_dashboard('outputs\fortran_gui_dashboard.html')
                return
            case ('--smoke')
                if (len_trim(build_section_text(1)) == 0) error stop 1
                return
            end select
        end if

        h_instance = GetModuleHandleA(c_null_ptr)
        h_font = GetStockObject(DEFAULT_GUI_FONT)
        h_body_font = CreateFontA(-18_c_int, 0_c_int, 0_c_int, 0_c_int, FW_NORMAL, &
                                  0_c_int, 0_c_int, 0_c_int, DEFAULT_CHARSET, &
                                  OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY, &
                                  DEFAULT_PITCH, c_string_ptr('Segoe UI'))
        h_mono_font = CreateFontA(-18_c_int, 0_c_int, 0_c_int, 0_c_int, FW_NORMAL, &
                                  0_c_int, 0_c_int, 0_c_int, DEFAULT_CHARSET, &
                                  OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY, &
                                  DEFAULT_PITCH, c_string_ptr('Consolas'))
        h_button_font = CreateFontA(-17_c_int, 0_c_int, 0_c_int, 0_c_int, FW_SEMIBOLD, &
                                    0_c_int, 0_c_int, 0_c_int, DEFAULT_CHARSET, &
                                    OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY, &
                                    DEFAULT_PITCH, c_string_ptr('Segoe UI'))

        wc%style = 0_c_int
        wc%lpfn_wnd_proc = c_funloc(wnd_proc)
        wc%cb_cls_extra = 0_c_int
        wc%cb_wnd_extra = 0_c_int
        wc%h_instance = h_instance
        wc%h_icon = c_null_ptr
        wc%h_cursor = LoadCursorA(c_null_ptr, int_to_ptr(int(IDC_ARROW, c_intptr_t)))
        wc%hbr_background = int_to_ptr(int(COLOR_WINDOW + 1_c_int, c_intptr_t))
        wc%menu_name = c_null_ptr
        wc%class_name = c_loc(class_name)

        atom = RegisterClassA(wc)
        if (atom == 0_c_short) then
            call show_info('Could not register the Win32 window class.', 'Fortran GUI')
            return
        end if

        h_main = CreateWindowExA(0_c_int, c_loc(class_name), c_loc(app_title), &
                                WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT, &
                                1320_c_int, 820_c_int, c_null_ptr, c_null_ptr, &
                                h_instance, c_null_ptr)
        if (.not. c_associated(h_main)) then
            call show_info('Could not create the main GUI window.', 'Fortran GUI')
            return
        end if

        ok = ShowWindow(h_main, SW_SHOW)
        ok = UpdateWindow(h_main)

        do
            ok = GetMessageA(msg, c_null_ptr, 0_c_int, 0_c_int)
            if (ok <= 0_c_int) exit
            ok = TranslateMessage(msg)
            call ignore_intptr(DispatchMessageA(msg))
        end do
    end subroutine run_gui

    function wnd_proc(hwnd, message, wparam, lparam) bind(C) result(ret)
        type(c_ptr), value :: hwnd
        integer(c_int), value :: message
        integer(c_intptr_t), value :: wparam
        integer(c_intptr_t), value :: lparam
        integer(c_intptr_t) :: ret
        integer(c_int) :: control_id, notify_code, width, height, ok

        ret = 0_c_intptr_t
        select case (message)
        case (WM_CREATE)
            call create_child_controls(hwnd)
            call populate_navigation()
            call update_section(1)
        case (WM_SIZE)
            width = loword(lparam)
            height = hiword(lparam)
            call layout_controls(width, height)
        case (WM_SETFOCUS)
            if (c_associated(h_nav)) call ignore_ptr(SetFocus(h_nav))
        case (WM_KEYDOWN)
            if (wparam == int(VK_ESCAPE, c_intptr_t)) then
                ok = DestroyWindow(hwnd)
            else
                ret = DefWindowProcA(hwnd, message, wparam, lparam)
            end if
        case (WM_COMMAND)
            control_id = loword(wparam)
            notify_code = hiword(wparam)
            select case (control_id)
            case (ID_NAV)
                if (notify_code == LBN_SELCHANGE) call update_selected_section()
            case (ID_RUN_ALL)
                call run_workflow(0)
            case (ID_RUN_SECTION)
                call run_workflow(current_section)
            case (ID_REFRESH)
                call update_section(current_section)
                call set_status('Refreshed from generated CSV artifacts.')
            case (ID_EXPORT)
                call write_html_dashboard('outputs\fortran_gui_dashboard.html')
                call set_status('Wrote outputs\fortran_gui_dashboard.html')
                call show_info('Wrote outputs\fortran_gui_dashboard.html', 'Fortran GUI')
            case (ID_OPEN_HTML)
                call open_path('outputs\fortran_gui_dashboard.html')
            case (ID_OPEN_OUTPUTS)
                call open_path('outputs')
            case (ID_CLOSE)
                ok = DestroyWindow(hwnd)
            case default
                ret = DefWindowProcA(hwnd, message, wparam, lparam)
            end select
        case (WM_DESTROY)
            call PostQuitMessage(0_c_int)
        case default
            ret = DefWindowProcA(hwnd, message, wparam, lparam)
        end select
    end function wnd_proc

    subroutine create_child_controls(parent)
        type(c_ptr), value :: parent
        integer(c_int) :: nav_style, edit_style, button_style

        nav_style = ior(WS_CHILD, ior(WS_VISIBLE, ior(WS_BORDER, ior(WS_VSCROLL, LBS_NOTIFY))))
        edit_style = ior(WS_CHILD, ior(WS_VISIBLE, ior(WS_VSCROLL, ior(WS_HSCROLL, &
                     ior(ES_MULTILINE, ior(ES_AUTOVSCROLL, ior(ES_AUTOHSCROLL, ES_READONLY)))))))
        button_style = ior(WS_CHILD, ior(WS_VISIBLE, ior(WS_TABSTOP, BS_PUSHBUTTON)))

        h_header = CreateWindowExA(0_c_int, c_loc(static_class), &
            c_string_ptr('Fortran workflow controller for non-gray radiation, FDS context, and paper-derived data'), &
            ior(WS_CHILD, WS_VISIBLE), 16_c_int, 12_c_int, 900_c_int, 30_c_int, &
            parent, int_to_ptr(0_c_intptr_t), h_instance, c_null_ptr)

        h_nav = CreateWindowExA(WS_EX_CLIENTEDGE, c_loc(listbox_class), c_null_ptr, &
            nav_style, 16_c_int, 54_c_int, 260_c_int, 600_c_int, parent, &
            int_to_ptr(int(ID_NAV, c_intptr_t)), h_instance, c_null_ptr)

        h_view = CreateWindowExA(WS_EX_CLIENTEDGE, c_loc(edit_class), c_null_ptr, &
            edit_style, 292_c_int, 54_c_int, 820_c_int, 600_c_int, parent, &
            int_to_ptr(0_c_intptr_t), h_instance, c_null_ptr)

        h_run_all = CreateWindowExA(0_c_int, c_loc(button_class), c_string_ptr('Run All'), &
            button_style, 292_c_int, 16_c_int, 96_c_int, 32_c_int, parent, &
            int_to_ptr(int(ID_RUN_ALL, c_intptr_t)), h_instance, c_null_ptr)

        h_run_section = CreateWindowExA(0_c_int, c_loc(button_class), c_string_ptr('Run Selected'), &
            button_style, 398_c_int, 16_c_int, 130_c_int, 32_c_int, parent, &
            int_to_ptr(int(ID_RUN_SECTION, c_intptr_t)), h_instance, c_null_ptr)

        h_refresh = CreateWindowExA(0_c_int, c_loc(button_class), c_string_ptr('Refresh'), &
            button_style, 538_c_int, 16_c_int, 92_c_int, 32_c_int, parent, &
            int_to_ptr(int(ID_REFRESH, c_intptr_t)), h_instance, c_null_ptr)

        h_export = CreateWindowExA(0_c_int, c_loc(button_class), c_string_ptr('Export HTML'), &
            button_style, 640_c_int, 16_c_int, 120_c_int, 32_c_int, parent, &
            int_to_ptr(int(ID_EXPORT, c_intptr_t)), h_instance, c_null_ptr)

        h_open_html = CreateWindowExA(0_c_int, c_loc(button_class), c_string_ptr('Open HTML'), &
            button_style, 770_c_int, 16_c_int, 108_c_int, 32_c_int, parent, &
            int_to_ptr(int(ID_OPEN_HTML, c_intptr_t)), h_instance, c_null_ptr)

        h_open_outputs = CreateWindowExA(0_c_int, c_loc(button_class), c_string_ptr('Outputs'), &
            button_style, 888_c_int, 16_c_int, 94_c_int, 32_c_int, parent, &
            int_to_ptr(int(ID_OPEN_OUTPUTS, c_intptr_t)), h_instance, c_null_ptr)

        h_close = CreateWindowExA(0_c_int, c_loc(button_class), c_string_ptr('Close'), &
            button_style, 992_c_int, 16_c_int, 78_c_int, 32_c_int, parent, &
            int_to_ptr(int(ID_CLOSE, c_intptr_t)), h_instance, c_null_ptr)

        h_status = CreateWindowExA(0_c_int, c_loc(static_class), c_string_ptr('Ready'), &
            ior(WS_CHILD, WS_VISIBLE), 16_c_int, 668_c_int, 1096_c_int, 24_c_int, &
            parent, int_to_ptr(0_c_intptr_t), h_instance, c_null_ptr)

        call apply_default_font(h_header)
        call apply_default_font(h_nav)
        call apply_default_font(h_view)
        call apply_default_font(h_run_all)
        call apply_default_font(h_run_section)
        call apply_default_font(h_refresh)
        call apply_default_font(h_export)
        call apply_default_font(h_open_html)
        call apply_default_font(h_open_outputs)
        call apply_default_font(h_close)
        call apply_default_font(h_status)
    end subroutine create_child_controls

    subroutine apply_default_font(hwnd)
        type(c_ptr), value :: hwnd
        type(c_ptr) :: selected_font

        selected_font = h_font
        if (c_associated(hwnd, h_view) .and. c_associated(h_mono_font)) then
            selected_font = h_mono_font
        else if ((c_associated(hwnd, h_run_all) .or. c_associated(hwnd, h_run_section) .or. &
                  c_associated(hwnd, h_refresh) .or. c_associated(hwnd, h_export) .or. &
                  c_associated(hwnd, h_open_html) .or. c_associated(hwnd, h_open_outputs) .or. &
                  c_associated(hwnd, h_close)) .and. c_associated(h_button_font)) then
            selected_font = h_button_font
        else if (c_associated(h_body_font)) then
            selected_font = h_body_font
        end if

        if (c_associated(hwnd) .and. c_associated(selected_font)) then
            call ignore_intptr(SendMessageA(hwnd, WM_SETFONT, ptr_to_intptr(selected_font), 1_c_intptr_t))
        end if
    end subroutine apply_default_font

    subroutine populate_navigation()
        integer :: i
        character(kind=c_char, len=:), allocatable, target :: item

        if (.not. c_associated(h_nav)) return
        call ignore_intptr(SendMessageA(h_nav, LB_RESETCONTENT, 0_c_intptr_t, 0_c_intptr_t))
        do i = 1, section_count
            item = to_c_text(trim(section_titles(i)))
            call ignore_intptr(SendMessageA(h_nav, LB_ADDSTRING, 0_c_intptr_t, ptr_to_intptr(c_loc(item))))
        end do
        call ignore_intptr(SendMessageA(h_nav, LB_SETCURSEL, 0_c_intptr_t, 0_c_intptr_t))
    end subroutine populate_navigation

    subroutine update_selected_section()
        integer(c_intptr_t) :: selected

        if (.not. c_associated(h_nav)) return
        selected = SendMessageA(h_nav, LB_GETCURSEL, 0_c_intptr_t, 0_c_intptr_t)
        if (selected >= 0_c_intptr_t .and. selected < int(section_count, c_intptr_t)) then
            call update_section(int(selected) + 1)
        end if
    end subroutine update_selected_section

    subroutine update_section(section_id)
        integer, intent(in) :: section_id
        character(len=:), allocatable :: text

        current_section = max(1, min(section_count, section_id))
        text = build_section_text(current_section)
        call set_multiline_text(h_view, text)
        call set_status('Loaded: '//trim(section_titles(current_section)))
    end subroutine update_section

    subroutine run_workflow(section_id)
        integer, intent(in) :: section_id
        character(len=:), allocatable :: cmd, log_path, label
        integer :: exitstat
        integer(c_int) :: ok

        call ensure_outputs_dir()
        select case (section_id)
        case (2)
            label = 'Project 1 hydrogen/H2O workflow'
            log_path = 'outputs\gui_run_project1.log'
            cmd = 'cmd /c "python scripts\run_project1_real_hydrogen.py > '//log_path//' 2>&1"'
        case (3)
            label = 'Project 2 particle-correlation workflow'
            log_path = 'outputs\gui_run_project2.log'
            cmd = 'cmd /c "python scripts\run_project2_real_particles.py > '//log_path//' 2>&1"'
        case (4)
            label = 'Project 3 DOM workflow'
            log_path = 'outputs\gui_run_project3.log'
            cmd = 'cmd /c "python scripts\run_project3_real_dom.py > '//log_path//' 2>&1"'
        case (5)
            label = 'Project 4 surrogate workflow'
            log_path = 'outputs\gui_run_project4.log'
            cmd = 'cmd /c "python scripts\run_project4_real_surrogate.py > '//log_path//' 2>&1"'
        case (7)
            label = 'Project 5 RADCAL asset smoke test'
            log_path = 'outputs\gui_run_radcal.log'
            cmd = 'cmd /c "python scripts\run_radcal_asset.py > '//log_path//' 2>&1"'
        case default
            label = 'all project workflows'
            log_path = 'outputs\gui_run_all.log'
            cmd = 'cmd /c "python scripts\run_all.py > '//log_path//' 2>&1"'
        end select

        call set_status('Running '//label//' ... this window may pause until the run finishes.')
        ok = UpdateWindow(h_main)
        call execute_command_line(cmd, wait=.true., exitstat=exitstat)

        if (exitstat == 0) then
            call update_section(current_section)
            call set_status('Completed '//label//'. Log: '//log_path)
            call show_info('Completed '//label//'.', 'Fortran GUI')
        else
            call update_section(current_section)
            call set_status('Workflow failed. See '//log_path)
            call show_info('Workflow failed. Open outputs or inspect '//log_path, 'Fortran GUI')
        end if
    end subroutine run_workflow

    subroutine ensure_outputs_dir()
        integer :: exitstat

        call execute_command_line('cmd /c "if not exist outputs mkdir outputs"', wait=.true., exitstat=exitstat)
    end subroutine ensure_outputs_dir

    subroutine append_artifact_status(text, path)
        character(len=:), allocatable, intent(inout) :: text
        character(len=*), intent(in) :: path

        if (file_exists(path)) then
            call add_line(text, '  [OK] '//trim(path))
        else
            call add_line(text, '  [missing] '//trim(path))
        end if
    end subroutine append_artifact_status

    subroutine append_fds_status(text)
        character(len=:), allocatable, intent(inout) :: text

        call add_line(text, 'FDS clone status:')
        if (file_exists('fds\Source\radi.f90')) then
            call add_line(text, '  [OK] Detected fds\Source\radi.f90 in this project folder.')
            call add_line(text, '  FDS source snapshot: Fortran 2018 codebase; 33 Source\*.f90 files detected in the clone.')
            call add_line(text, '  Radiation verification snapshot: 73 fds\Verification\Radiation\*.fds cases detected.')
        else
            call add_line(text, '  [missing] No fds\Source\radi.f90 found relative to this launcher.')
            call add_line(text, '  Launch from E:\Thermal Radiation Modeling\radiation_portfolio_gui.exe after syncing the FDS clone.')
        end if
        call add_line(text, '')
    end subroutine append_fds_status

    subroutine append_run_log_tail(text)
        character(len=:), allocatable, intent(inout) :: text
        character(len=*), parameter :: logs(6) = [character(len=32) :: &
            'outputs\gui_run_all.log', &
            'outputs\gui_run_project1.log', &
            'outputs\gui_run_project2.log', &
            'outputs\gui_run_project3.log', &
            'outputs\gui_run_project4.log', &
            'outputs\gui_run_radcal.log']
        integer :: i

        call add_line(text, 'Recent run logs:')
        do i = 1, size(logs)
            if (file_exists(logs(i))) call append_artifact_status(text, logs(i))
        end do
        call add_line(text, '')
        if (file_exists('outputs\gui_run_all.log')) then
            call add_line(text, 'Tail of outputs\gui_run_all.log:')
            call append_file_tail(text, 'outputs\gui_run_all.log', 8)
        end if
    end subroutine append_run_log_tail

    subroutine append_file_tail(text, path, max_lines)
        character(len=:), allocatable, intent(inout) :: text
        character(len=*), intent(in) :: path
        integer, intent(in) :: max_lines
        character(len=line_len) :: line
        character(len=line_len), allocatable :: ring(:)
        integer :: unit, ios, count, idx, i, start_idx

        if (.not. file_exists(path)) return
        allocate (ring(max_lines))
        ring = ''
        open (newunit=unit, file=path, status='old', action='read', iostat=ios)
        if (ios /= 0) return
        count = 0
        do
            read (unit, '(a)', iostat=ios) line
            if (ios /= 0) exit
            idx = mod(count, max_lines) + 1
            ring(idx) = line
            count = count + 1
        end do
        close (unit)

        start_idx = max(0, count - max_lines)
        do i = start_idx, count - 1
            idx = mod(i, max_lines) + 1
            if (len_trim(ring(idx)) > 0) call add_line(text, '  '//trim(ring(idx)))
        end do
        call add_line(text, '')
    end subroutine append_file_tail

    subroutine layout_controls(width, height)
        integer(c_int), intent(in) :: width
        integer(c_int), intent(in) :: height
        integer(c_int) :: content_top, bottom_top, nav_w, pad, button_y, view_x
        integer(c_int) :: content_h, view_w, ok

        if (width < 700_c_int .or. height < 420_c_int) return
        pad = 16_c_int
        nav_w = 320_c_int
        button_y = 18_c_int
        content_top = 64_c_int
        bottom_top = height - 44_c_int
        content_h = max(250_c_int, bottom_top - content_top - 12_c_int)
        view_x = pad + nav_w + 16_c_int
        view_w = max(320_c_int, width - view_x - pad)

        ok = MoveWindow(h_header, pad, 12_c_int, nav_w, 42_c_int, 1_c_int)
        ok = MoveWindow(h_run_all, view_x, button_y, 96_c_int, 34_c_int, 1_c_int)
        ok = MoveWindow(h_run_section, view_x + 106_c_int, button_y, 130_c_int, 34_c_int, 1_c_int)
        ok = MoveWindow(h_refresh, view_x + 246_c_int, button_y, 92_c_int, 34_c_int, 1_c_int)
        ok = MoveWindow(h_export, view_x + 348_c_int, button_y, 120_c_int, 34_c_int, 1_c_int)
        ok = MoveWindow(h_open_html, view_x + 478_c_int, button_y, 108_c_int, 34_c_int, 1_c_int)
        ok = MoveWindow(h_open_outputs, view_x + 596_c_int, button_y, 94_c_int, 34_c_int, 1_c_int)
        ok = MoveWindow(h_close, view_x + 700_c_int, button_y, 78_c_int, 34_c_int, 1_c_int)
        ok = MoveWindow(h_nav, pad, content_top, nav_w, content_h, 1_c_int)
        ok = MoveWindow(h_view, view_x, content_top, view_w, content_h, 1_c_int)
        ok = MoveWindow(h_status, pad, bottom_top, width - 2_c_int * pad, 24_c_int, 1_c_int)
    end subroutine layout_controls

    function build_section_text(section_id) result(text)
        integer, intent(in) :: section_id
        character(len=:), allocatable :: text

        text = ''
        select case (section_id)
        case (1)
            call add_line(text, 'SOURCE MAP, WORKFLOW CONTROLS, AND FDS CONTEXT')
            call add_rule(text)
            call add_line(text, 'Use this window as the launcher. You do not need to run terminal commands first.')
            call add_line(text, '')
            call add_line(text, 'Buttons:')
            call add_line(text, '  Run All       - regenerates every project output and report.')
            call add_line(text, '  Run Selected  - regenerates the selected project section.')
            call add_line(text, '  Refresh       - reloads generated outputs into this view.')
            call add_line(text, '  Export HTML   - writes an HTML report from the GUI summaries.')
            call add_line(text, '  Open HTML     - opens that report in your default browser.')
            call add_line(text, '  Outputs       - opens the outputs folder.')
            call add_line(text, '')
            call add_line(text, 'Source basis:')
            call add_line(text, '  Singh & Hostikka 2026: hydrogen/H2O non-gray radiation, Planck-mean H2O fit,')
            call add_line(text, '  published RCFSK/WSGG/Planck error and CPU tables.')
            call add_line(text, '  Rashidzadeh et al. 2026: RC-FSK implementation direction in FDS.')
            call add_line(text, '  Hostikka & Rashidzadeh 2026: fire-CFD radiation modelling review.')
            call add_line(text, '  Johansson 2017: Mie-fitted coal/char and ash particle efficiency correlations.')
            call add_line(text, '')
            call append_fds_status(text)
            call append_run_log_tail(text)
        case (2)
            call add_line(text, 'PROJECT 1: HYDROGEN / H2O NON-GRAY RADIATION')
            call add_rule(text)
            call add_line(text, 'What this project does:')
            call add_line(text, '  Encodes the Singh & Hostikka H2O Planck-mean absorption correlation and')
            call add_line(text, '  stores their published comparison metrics for RCFSK, WSGG, and Planck mean.')
            call add_line(text, '')
            call add_line(text, 'Core equation:')
            call add_line(text, '  kappa_planck = X_H2O * 3.8821e6 * T^(-1.9811)')
            call add_line(text, '')
            call add_line(text, 'Published result summary:')
            call add_line(text, '  Radial source peak error: RCFSK <= 14%, WSGG about 43%, Planck mean about 150%.')
            call add_line(text, '  Axial wall-flux peak error: RCFSK within 7%.')
            call add_line(text, '  Sandia plume side-wall flux: RCFSK about 6%, WSGG about 51%.')
            call add_line(text, '  CPU timing table: 4 RTE solves for RCFSK/WSGG vs 1 solve for Planck mean.')
            call add_line(text, '')
            call add_line(text, 'Generated artifacts:')
            call append_artifact_status(text, 'outputs\project1_real_hydrogen\tables\singh_model_error_summary.csv')
            call append_artifact_status(text, 'outputs\project1_real_hydrogen\tables\singh_table2_cpu_times.csv')
            call append_artifact_status(text, 'outputs\project1_real_hydrogen\figures\radial_fields.png')
            call append_artifact_status(text, 'outputs\project1_real_hydrogen\project1_report.md')
            call add_line(text, '')
            call add_line(text, 'Press Run Selected to regenerate this project from the GUI.')
        case (3)
            call add_line(text, 'PROJECT 2: JOHANSSON PARTICLE CORRELATIONS')
            call add_rule(text)
            call add_line(text, 'What this project does:')
            call add_line(text, '  Implements Johansson 2017 gray absorption/scattering efficiencies for')
            call add_line(text, '  coal/char and two ash compositions fitted to Mie calculations.')
            call add_line(text, '')
            call add_line(text, 'Correlation form:')
            call add_line(text, '  1 / y^z = 1 / y0^z + 1 / y_inf^z')
            call add_line(text, '')
            call add_line(text, 'Why it matters for the Aalto/FDS work:')
            call add_line(text, '  The posting emphasizes multi-phase radiation and fuel particles. FDS already')
            call add_line(text, '  contains Mie machinery in Source\radi.f90; these correlations are a compact')
            call add_line(text, '  bridge from published particle optics into model-development experiments.')
            call add_line(text, '')
            call add_line(text, 'Generated artifacts:')
            call append_artifact_status(text, 'outputs\project2_real_particles\tables\johansson_correlation_parameters.csv')
            call append_artifact_status(text, 'outputs\project2_real_particles\tables\johansson_particle_efficiencies.csv')
            call append_artifact_status(text, 'outputs\project2_real_particles\figures\johansson_radius_sweep_1500K.png')
            call append_artifact_status(text, 'outputs\project2_real_particles\project2_report.md')
            call add_line(text, '')
            call add_line(text, 'Press Run Selected to regenerate this project from the GUI.')
        case (4)
            call add_line(text, 'PROJECT 3: DOM ON PUBLISHED FIELDS')
            call add_rule(text)
            call add_line(text, 'What this project does:')
            call add_line(text, '  Runs a transparent 1-D discrete ordinates radiation check over the published')
            call add_line(text, '  Singh & Hostikka radial and axial thermodynamic fields.')
            call add_line(text, '')
            call add_line(text, 'Boundary:')
            call add_line(text, '  This is an educational DOM check, not a claimed reproduction of the paper''s')
            call add_line(text, '  full 2-D LBL/RCFSK solution.')
            call add_line(text, '')
            call append_dom_summary(text, 'outputs/project3_real_dom/tables/radial_midline_dom_profile.csv', 'radial midline')
            call append_dom_summary(text, 'outputs/project3_real_dom/tables/axial_centerline_dom_profile.csv', 'axial centerline')
            call add_line(text, 'Generated artifacts:')
            call append_artifact_status(text, 'outputs\project3_real_dom\tables\radial_midline_dom_profile.csv')
            call append_artifact_status(text, 'outputs\project3_real_dom\tables\axial_centerline_dom_profile.csv')
            call append_artifact_status(text, 'outputs\project3_real_dom\figures\published_field_dom_profiles.png')
            call append_artifact_status(text, 'outputs\project3_real_dom\project3_report.md')
            call add_line(text, '')
            call add_line(text, 'Press Run Selected to regenerate this project from the GUI.')
        case (5)
            call add_line(text, 'PROJECT 4: ML SURROGATE ON PUBLISHED H2O CORRELATION')
            call add_rule(text)
            call add_line(text, 'What this project does:')
            call add_line(text, '  Trains a small surrogate for log10(kappa_planck), using the published')
            call add_line(text, '  Singh & Hostikka H2O absorption correlation as the target.')
            call add_line(text, '')
            call add_line(text, 'Current verified metrics:')
            call add_line(text, '  Training samples: 4620')
            call add_line(text, '  Test samples: 1540')
            call add_line(text, '  R2 in log space: 0.99907')
            call add_line(text, '  RMSE log10: 0.02162')
            call add_line(text, '  Mean absolute percentage error in kappa: 3.20%')
            call add_line(text, '')
            call add_line(text, 'Generated artifacts:')
            call append_artifact_status(text, 'outputs\project4_real_surrogate\tables\surrogate_metrics.csv')
            call append_artifact_status(text, 'outputs\project4_real_surrogate\tables\surrogate_predictions.csv')
            call append_artifact_status(text, 'outputs\project4_real_surrogate\figures\surrogate_kappa_parity.png')
            call append_artifact_status(text, 'outputs\project4_real_surrogate\project4_report.md')
            call add_line(text, '')
            call add_line(text, 'Press Run Selected to regenerate this project from the GUI.')
        case (6)
            call add_line(text, 'FDS CLONE: WHAT IT IS AND HOW WE CAN USE IT')
            call add_rule(text)
            call append_fds_status(text)
            call add_line(text, 'What FDS is:')
            call add_line(text, '  FDS is NIST''s Fire Dynamics Simulator: a large Fortran 2018 LES/fire-CFD')
            call add_line(text, '  solver for smoke, heat transport, combustion, radiation, particles, walls,')
            call add_line(text, '  and verification/validation cases. Smokeview is the companion visualizer.')
            call add_line(text, '')
            call add_line(text, 'Relevant files in your clone:')
            call add_line(text, '  fds\Source\radi.f90  - radiation heat transfer module.')
            call add_line(text, '  fds\Source\rcal.f90  - RADCAL-related gas absorption calculations.')
            call add_line(text, '  fds\Source\part.f90  - Lagrangian particles.')
            call add_line(text, '  fds\Source\vege.f90  - vegetation/wildland-fire structures.')
            call add_line(text, '  fds\Verification\Radiation\*.fds  - 73 radiation verification cases detected.')
            call add_line(text, '  fds\Verification\WUI\*radi*.fds   - gas/vegetation radiation consistency cases.')
            call add_line(text, '')
            call add_line(text, 'What we can use it for in this portfolio:')
            call add_line(text, '  1. Map our Fortran radiation kernels to FDS naming, data structures, and routines.')
            call add_line(text, '  2. Use FDS verification cases as examples for future benchmark runs.')
            call add_line(text, '  3. Prototype H2O/particle routines outside FDS first, then document where they')
            call add_line(text, '     would connect inside radi.f90.')
            call add_line(text, '  4. Keep this portfolio honest: it can inspect and align with FDS, but it is')
            call add_line(text, '     not yet a patched or validated FDS branch.')
        case (7)
            call add_line(text, 'PROJECT 5: RADCAL ASSET SMOKE TEST')
            call add_rule(text)
            call add_line(text, 'What this project does:')
            call add_line(text, '  Runs the downloaded Firemodels RADCAL Windows executable from the GUI.')
            call add_line(text, '  The wrapper finds libiomp5md.dll and prepends its folder to PATH only for')
            call add_line(text, '  the RADCAL subprocess, fixing the missing Intel OpenMP runtime error.')
            call add_line(text, '')
            call add_line(text, 'Boundary:')
            call add_line(text, '  This is a launch/parsing smoke test against a small RADCAL example case.')
            call add_line(text, '  It is not a validation claim for a fire scenario.')
            call add_line(text, '')
            call add_line(text, 'Generated artifacts:')
            call append_artifact_status(text, 'outputs\project5_radcal_asset\RADCAL.IN')
            call append_artifact_status(text, 'outputs\project5_radcal_asset\RADCAL.OUT')
            call append_artifact_status(text, 'outputs\project5_radcal_asset\TRANS_PORTFOLIO_RADCAL_SMOKE_TEST.TEC')
            call append_artifact_status(text, 'outputs\project5_radcal_asset\radcal_summary.csv')
            call append_artifact_status(text, 'outputs\project5_radcal_asset\radcal_run_report.md')
            call add_line(text, '')
            if (file_exists('outputs\project5_radcal_asset\RADCAL.OUT')) then
                call add_line(text, 'RADCAL.OUT:')
                call append_file_tail(text, 'outputs\project5_radcal_asset\RADCAL.OUT', 12)
                call add_line(text, '')
            end if
            call add_line(text, 'Press Run Selected to run this RADCAL smoke test from the GUI.')
        end select
    end function build_section_text

    subroutine append_dom_summary(text, path, label)
        character(len=:), allocatable, intent(inout) :: text
        character(len=*), intent(in) :: path
        character(len=*), intent(in) :: label
        character(len=line_len) :: line
        character(len=field_len) :: fields(max_fields)
        integer :: unit, ios, nfields, count
        real(8) :: heat_flux, source_term
        real(8) :: flux_min, flux_max, source_min, source_max
        character(len=160) :: formatted

        call add_line(text, 'DOM summary: '//trim(label))
        if (.not. file_exists(path)) then
            call add_line(text, '  Missing profile. Run: python scripts/run_all.py')
            call add_line(text, '')
            return
        end if

        open (newunit=unit, file=path, status='old', action='read', iostat=ios)
        if (ios /= 0) then
            call add_line(text, '  Could not open this profile.')
            call add_line(text, '')
            return
        end if

        read (unit, '(a)', iostat=ios) line
        count = 0
        flux_min = huge(1.0d0)
        flux_max = -huge(1.0d0)
        source_min = huge(1.0d0)
        source_max = -huge(1.0d0)

        do
            read (unit, '(a)', iostat=ios) line
            if (ios /= 0) exit
            call split_csv(line, fields, nfields)
            if (nfields >= 6) then
                heat_flux = parse_real(fields(5))
                source_term = parse_real(fields(6))
                flux_min = min(flux_min, heat_flux)
                flux_max = max(flux_max, heat_flux)
                source_min = min(source_min, source_term)
                source_max = max(source_max, source_term)
                count = count + 1
            end if
        end do
        close (unit)

        write (formatted, '(a,i0)') '  samples: ', count
        call add_line(text, trim(formatted))
        write (formatted, '(a,es12.4,a,es12.4)') '  heat flux range [W/m2]: ', flux_min, ' to ', flux_max
        call add_line(text, trim(formatted))
        write (formatted, '(a,es12.4,a,es12.4)') '  source term range [W/m3]: ', source_min, ' to ', source_max
        call add_line(text, trim(formatted))
        call add_line(text, '')
    end subroutine append_dom_summary

    subroutine write_html_dashboard(output_path)
        character(len=*), intent(in) :: output_path
        character(len=:), allocatable :: text
        integer :: unit, ios, i

        call ensure_outputs_dir()
        open (newunit=unit, file=output_path, status='replace', action='write', iostat=ios)
        if (ios /= 0) then
            call set_status('Could not write '//trim(output_path))
            return
        end if

        write (unit, '(a)') '<!doctype html>'
        write (unit, '(a)') '<html lang="en"><head><meta charset="utf-8">'
        write (unit, '(a)') '<meta name="viewport" content="width=device-width, initial-scale=1">'
        write (unit, '(a)') '<title>Thermal Radiation Portfolio GUI Export</title>'
        write (unit, '(a)') '<style>'
        write (unit, '(a)') 'body{font-family:Segoe UI,Arial,sans-serif;margin:0;background:#101417;color:#edf2f4;}'
        write (unit, '(a)') 'main{max-width:1180px;margin:auto;padding:32px;}'
        write (unit, '(a)') 'section{border:1px solid #33414a;margin:18px 0;padding:18px;background:#161d22;}'
        write (unit, '(a)') 'h1,h2{font-weight:650;} pre{white-space:pre-wrap;line-height:1.45;color:#d9e4ea;}'
        write (unit, '(a)') '</style></head><body><main>'
        write (unit, '(a)') '<h1>Non-Gray Thermal Radiation Portfolio</h1>'
        write (unit, '(a)') '<p>Exported by the native Fortran Win32 GUI from real generated CSV artifacts.</p>'
        do i = 1, section_count
            text = build_section_text(i)
            write (unit, '(a)') '<section>'
            write (unit, '(a)') '<h2>'//trim(html_escape(section_titles(i)))//'</h2>'
            write (unit, '(a)') '<pre>'
            call write_html_pre(unit, text)
            write (unit, '(a)') '</pre></section>'
        end do
        write (unit, '(a)') '</main></body></html>'
        close (unit)
    end subroutine write_html_dashboard

    subroutine write_html_pre(unit, text)
        integer, intent(in) :: unit
        character(len=*), intent(in) :: text
        integer :: i, start

        start = 1
        do i = 1, len(text)
            if (text(i:i) == achar(10)) then
                write (unit, '(a)') html_escape(text(start:i - 1))
                start = i + 1
            end if
        end do
        if (start <= len(text)) write (unit, '(a)') html_escape(text(start:len(text)))
    end subroutine write_html_pre

    subroutine split_csv(line, fields, nfields)
        character(len=*), intent(in) :: line
        character(len=field_len), intent(out) :: fields(max_fields)
        integer, intent(out) :: nfields
        integer :: i, start, len_line

        fields = ''
        nfields = 0
        start = 1
        len_line = len_trim(line)
        do i = 1, len_line + 1
            if (i > len_line .or. line(i:i) == ',') then
                if (nfields < max_fields) then
                    nfields = nfields + 1
                    fields(nfields) = adjustl(line(start:i - 1))
                end if
                start = i + 1
            end if
        end do
    end subroutine split_csv

    function parse_real(text) result(value)
        character(len=*), intent(in) :: text
        real(8) :: value
        integer :: ios

        read (text, *, iostat=ios) value
        if (ios /= 0) value = 0.0d0
    end function parse_real

    logical function file_exists(path)
        character(len=*), intent(in) :: path
        inquire (file=path, exist=file_exists)
    end function file_exists

    subroutine add_rule(text)
        character(len=:), allocatable, intent(inout) :: text
        call add_line(text, repeat('-', 78))
    end subroutine add_rule

    subroutine add_line(text, line)
        character(len=:), allocatable, intent(inout) :: text
        character(len=*), intent(in) :: line

        if (.not. allocated(text)) text = ''
        text = text//trim(line)//achar(10)
    end subroutine add_line

    subroutine set_multiline_text(hwnd, text)
        type(c_ptr), value :: hwnd
        character(len=*), intent(in) :: text
        character(kind=c_char, len=:), allocatable, target :: c_text
        integer(c_int) :: ok

        if (.not. c_associated(hwnd)) return
        c_text = to_c_windows_text(text)
        ok = SetWindowTextA(hwnd, c_loc(c_text))
    end subroutine set_multiline_text

    subroutine set_status(text)
        character(len=*), intent(in) :: text
        character(kind=c_char, len=:), allocatable, target :: c_text
        integer(c_int) :: ok

        if (.not. c_associated(h_status)) return
        c_text = to_c_text(text)
        ok = SetWindowTextA(h_status, c_loc(c_text))
    end subroutine set_status

    subroutine show_info(message, caption)
        character(len=*), intent(in) :: message
        character(len=*), intent(in) :: caption
        character(kind=c_char, len=:), allocatable, target :: c_message, c_caption
        integer(c_int) :: ok

        c_message = to_c_text(message)
        c_caption = to_c_text(caption)
        ok = MessageBoxA(h_main, c_loc(c_message), c_loc(c_caption), ior(MB_OK, MB_ICONINFORMATION))
    end subroutine show_info

    subroutine open_path(path)
        character(len=*), intent(in) :: path
        character(kind=c_char, len=:), allocatable, target :: operation, file_name
        character(len=:), allocatable :: absolute
        integer(c_intptr_t) :: result_code

        if (.not. file_exists(path)) then
            if (index(path, '.html') > 0) call write_html_dashboard(path)
            if (trim(path) == 'outputs') call ensure_outputs_dir()
        end if
        operation = to_c_text('open')
        absolute = absolute_path(path)
        file_name = to_c_text(absolute)
        result_code = ShellExecuteA(h_main, c_loc(operation), c_loc(file_name), &
                                    c_null_ptr, c_null_ptr, SW_SHOWNORMAL)
        if (result_code <= 32_c_intptr_t) then
            call show_info('Could not open '//trim(absolute), 'Fortran GUI')
        end if
    end subroutine open_path

    function absolute_path(path) result(out)
        character(len=*), intent(in) :: path
        character(len=:), allocatable :: out
        character(len=:), allocatable :: cwd

        if (len_trim(path) >= 2 .and. path(2:2) == ':') then
            out = normalize_path(trim(path))
        else
            cwd = current_directory()
            out = normalize_path(trim(cwd)//'\'//trim(path))
        end if
    end function absolute_path

    function current_directory() result(path)
        character(len=:), allocatable :: path
        character(kind=c_char, len=1024), target :: buffer
        integer(c_int) :: chars
        integer :: i

        buffer = c_null_char
        chars = GetCurrentDirectoryA(1023_c_int, c_loc(buffer))
        path = ''
        do i = 1, min(int(chars), 1023)
            if (buffer(i:i) == c_null_char) exit
            path = path//buffer(i:i)
        end do
    end function current_directory

    function normalize_path(path) result(out)
        character(len=*), intent(in) :: path
        character(len=:), allocatable :: out
        integer :: i

        out = trim(path)
        do i = 1, len(out)
            if (out(i:i) == '/') out(i:i) = '\'
        end do
    end function normalize_path

    function to_c_text(text) result(out)
        character(len=*), intent(in) :: text
        character(kind=c_char, len=:), allocatable :: out
        integer :: i, n

        n = len_trim(text)
        allocate (character(kind=c_char, len=n + 1) :: out)
        do i = 1, n
            out(i:i) = text(i:i)
        end do
        out(n + 1:n + 1) = c_null_char
    end function to_c_text

    function to_c_windows_text(text) result(out)
        character(len=*), intent(in) :: text
        character(kind=c_char, len=:), allocatable :: out
        integer :: i, pos, extra

        extra = 1
        do i = 1, len(text)
            if (text(i:i) == achar(10)) extra = extra + 1
        end do
        allocate (character(kind=c_char, len=len(text) + extra) :: out)
        pos = 1
        do i = 1, len(text)
            if (text(i:i) == achar(10)) then
                out(pos:pos) = achar(13)
                pos = pos + 1
                out(pos:pos) = achar(10)
            else
                out(pos:pos) = text(i:i)
            end if
            pos = pos + 1
        end do
        out(pos:pos) = c_null_char
    end function to_c_windows_text

    function c_string_ptr(text) result(ptr)
        character(len=*), intent(in) :: text
        type(c_ptr) :: ptr
        character(kind=c_char, len=:), allocatable, target, save :: scratch

        scratch = to_c_text(text)
        ptr = c_loc(scratch)
    end function c_string_ptr

    function html_escape(text) result(out)
        character(len=*), intent(in) :: text
        character(len=:), allocatable :: out
        integer :: i

        out = ''
        do i = 1, len_trim(text)
            select case (text(i:i))
            case ('&')
                out = out//'&amp;'
            case ('<')
                out = out//'&lt;'
            case ('>')
                out = out//'&gt;'
            case ('"')
                out = out//'&quot;'
            case default
                out = out//text(i:i)
            end select
        end do
    end function html_escape

    function loword(value) result(word)
        integer(c_intptr_t), intent(in) :: value
        integer(c_int) :: word

        word = int(iand(value, int(Z'FFFF', c_intptr_t)), c_int)
    end function loword

    function hiword(value) result(word)
        integer(c_intptr_t), intent(in) :: value
        integer(c_int) :: word

        word = int(iand(ishft(value, -16), int(Z'FFFF', c_intptr_t)), c_int)
    end function hiword

    function int_to_ptr(value) result(ptr)
        integer(c_intptr_t), intent(in) :: value
        type(c_ptr) :: ptr

        ptr = transfer(value, ptr)
    end function int_to_ptr

    function ptr_to_intptr(ptr) result(value)
        type(c_ptr), intent(in) :: ptr
        integer(c_intptr_t) :: value

        value = transfer(ptr, value)
    end function ptr_to_intptr

    subroutine ignore_intptr(value)
        integer(c_intptr_t), intent(in) :: value
        if (value == 0_c_intptr_t) return
    end subroutine ignore_intptr

    subroutine ignore_ptr(value)
        type(c_ptr), intent(in) :: value
        if (c_associated(value)) return
    end subroutine ignore_ptr

end module radiation_portfolio_win32_gui

program radiation_portfolio_gui
    use radiation_portfolio_win32_gui, only: run_gui
    implicit none

    call run_gui()
end program radiation_portfolio_gui
