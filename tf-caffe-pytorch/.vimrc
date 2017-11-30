set nocompatible              " be iMproved, required
filetype off                  " required

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')

" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'

" The following are examples of different formats supported.
" Keep Plugin commands between vundle#begin/end.
" plugin on GitHub repo
Plugin 'tpope/vim-fugitive'
" add nerdtree
Plugin 'scrooloose/nerdtree'
autocmd StdinReadPre * let s:std_in=1
autocmd VimEnter * if argc() == 0 && !exists("s:std_in") | NERDTree | endif
map <C-n> :NERDTreeToggle<CR>
let g:NERDTreeDirArrowExpandable = '>'
let g:NERDTreeDirArrowCollapsible = 'v'
" add nerdtree-tabs
Plugin 'jistr/vim-nerdtree-tabs'
map <Leader>n <plug>NERDTreeTabsToggle<CR>
" Add syntastic
Plugin 'vim-syntastic/syntastic'
set statusline+=%#warningmsg#
set statusline+=%{SyntasticStatuslineFlag()}
set statusline+=%*
let g:syntastic_always_populate_loc_list = 1
let g:syntastic_auto_loc_list = 1
let g:syntastic_check_on_open = 1
let g:syntastic_check_on_wq = 0
" Add Easy Motion
Plugin 'easymotion/vim-easymotion'
let g:EasyMotion_do_mapping = 0 " Disable default mappings
nmap s <Plug>(easymotion-overwin-f2)
map <Leader> <Plug>(easymotion-prefix)
let g:EasyMotion_smartcase = 1
map <Leader>j <Plug>(easymotion-j)
map <Leader>k <Plug>(easymotion-k)
" Add ctrlp
Plugin 'kien/ctrlp.vim'
let g:ctrlp_map = '<c-p>'
let g:ctrlp_cmd = 'CtrlP'
" Add airline
Plugin 'vim-airline/vim-airline'
Plugin 'vim-airline/vim-airline-themes'
set expandtab ts=4 sw=4 ai
set ic
set nowrap
set hlsearch
set nu
set laststatus=2
set enc=utf-8
set t_Co=256
" Add YouCompleteMe
Plugin 'Valloric/YouCompleteMe'
" Add Dockerfile.vim
Plugin 'kertansul/Dockerfile.vim'
" add colorschemes
Plugin 'flazz/vim-colorschemes'
silent! colorscheme molokai
" add tmux-navigator
"Plugin 'christoomey/vim-tmux-navigator'
"let g:tmux_navigator_no_mappings = 1
"nnoremap <silent> {Left-Mapping} :TmuxNavigateLeft<cr>
"nnoremap <silent> {Down-Mapping} :TmuxNavigateDown<cr>
"nnoremap <silent> {Up-Mapping} :TmuxNavigateUp<cr>
"nnoremap <silent> {Right-Mapping} :TmuxNavigateRight<cr>
"nnoremap <silent> {Previous-Mapping} :TmuxNavigatePrevious<cr>

" All of your Plugins must be added before the following line
call vundle#end()            " required
filetype plugin indent on    " required
" To ignore plugin indent changes, instead use:
"filetype plugin on
"
" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal
"
" see :h vundle for more details or wiki for FAQ
" Put your non-Plugin stuff after this line
"

" enable cursor highlight
set cursorline
set cursorcolumn
