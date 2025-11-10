import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import json

base_url="https://docs.python.org/3/"
visited_urls = set()
output_dir = Path("data/docs")
output_dir.mkdir(parents=True, exist_ok=True)

def parse_url(url):
    try:
        responce = requests.get(url, timeout=10)
        res = BeautifulSoup(responce.text, 'html.parser')
        for element in res.find_all(['nav', 'aside', 'footer', 'script', 'style']):
            element.decompose()
        main_content = res.find('div', {'class': 'body'}) or res.find('main') or res.find('article')
        if not main_content:
            main_content = res.find('body')
        chunks = []
        for element in main_content.find_all(['p', 'pre', 'h2', 'h3', 'dl']):
            text = element.get_text(strip=True)
            if text and len(text) > 20:
                chunks.append(text)
        title = res.find('h1')
        title = title.get_text(strip=True) if title else "No title"
        return {
            'url': url,
            'title': title,
            'content': '\n\n'.join(chunks)
        }
    except Exception as e:
        print(f'Error processing{url}: {e}')
        return None
    
def scrape_all_sections():
    important_urls = [
    # ==================== TUTORIAL ====================
    f"{base_url}tutorial/index.html",
    f"{base_url}tutorial/appetite.html",
    f"{base_url}tutorial/interpreter.html",
    f"{base_url}tutorial/introduction.html",
    f"{base_url}tutorial/controlflow.html",
    f"{base_url}tutorial/datastructures.html",  # Lists, dicts, comprehensions
    f"{base_url}tutorial/modules.html",
    f"{base_url}tutorial/inputoutput.html",  # File I/O, formatting
    f"{base_url}tutorial/errors.html",  # Exception handling
    f"{base_url}tutorial/classes.html",  # OOP
    f"{base_url}tutorial/stdlib.html",
    f"{base_url}tutorial/stdlib2.html",
    f"{base_url}tutorial/venv.html",  # Virtual environments
    f"{base_url}tutorial/whatnow.html",
    
    # ==================== LIBRARY - BUILT-IN ====================
    f"{base_url}library/index.html",
    f"{base_url}library/intro.html",
    f"{base_url}library/functions.html",  # Built-in functions (open, print, etc.)
    f"{base_url}library/constants.html",  # True, False, None, etc.
    f"{base_url}library/stdtypes.html",  # str, int, list, dict, set, etc.
    f"{base_url}library/exceptions.html",  # Exception hierarchy
    
    # ==================== TEXT PROCESSING ====================
    f"{base_url}library/string.html",  # String operations
    f"{base_url}library/re.html",  # Regular expressions
    f"{base_url}library/difflib.html",  # String diff utilities
    f"{base_url}library/textwrap.html",  # Text wrapping
    f"{base_url}library/unicodedata.html",  # Unicode database
    f"{base_url}library/stringprep.html",  # String preparation
    f"{base_url}library/readline.html",  # GNU readline
    f"{base_url}library/rlcompleter.html",  # Completion
    
    # ==================== BINARY DATA ====================
    f"{base_url}library/struct.html",  # Binary data structures
    f"{base_url}library/codecs.html",  # Codec registry and base classes
    
    # ==================== DATA TYPES ====================
    f"{base_url}library/datetime.html",  # Date and time
    f"{base_url}library/zoneinfo.html",  # Time zones
    f"{base_url}library/calendar.html",  # Calendar functions
    f"{base_url}library/collections.html",  # Container datatypes (deque, Counter, etc.)
    f"{base_url}library/collections.abc.html",  # Abstract base classes
    f"{base_url}library/heapq.html",  # Heap queue algorithm
    f"{base_url}library/bisect.html",  # Array bisection algorithm
    f"{base_url}library/array.html",  # Efficient arrays
    f"{base_url}library/weakref.html",  # Weak references
    f"{base_url}library/types.html",  # Dynamic type creation
    f"{base_url}library/copy.html",  # Shallow and deep copy
    f"{base_url}library/pprint.html",  # Pretty-print
    f"{base_url}library/reprlib.html",  # Alternate repr()
    f"{base_url}library/enum.html",  # Enumerations
    f"{base_url}library/graphlib.html",  # Graph operations
    
    # ==================== NUMERIC & MATH ====================
    f"{base_url}library/numbers.html",  # Numeric abstract base classes
    f"{base_url}library/math.html",  # Mathematical functions
    f"{base_url}library/cmath.html",  # Complex number math
    f"{base_url}library/decimal.html",  # Decimal fixed point arithmetic
    f"{base_url}library/fractions.html",  # Rational numbers
    f"{base_url}library/random.html",  # Random number generation
    f"{base_url}library/statistics.html",  # Statistical functions
    
    # ==================== FUNCTIONAL PROGRAMMING ====================
    f"{base_url}library/itertools.html",  # Iterator building blocks
    f"{base_url}library/functools.html",  # Higher-order functions (decorators, etc.)
    f"{base_url}library/operator.html",  # Standard operators as functions
    
    # ==================== FILE & DIRECTORY ====================
    f"{base_url}library/pathlib.html",  # Object-oriented filesystem paths
    f"{base_url}library/os.path.html",  # Common pathname manipulations
    f"{base_url}library/fileinput.html",  # Iterate over input lines
    f"{base_url}library/stat.html",  # Interpreting stat() results
    f"{base_url}library/filecmp.html",  # File and directory comparisons
    f"{base_url}library/tempfile.html",  # Temporary files and directories
    f"{base_url}library/glob.html",  # Unix style pathname pattern expansion
    f"{base_url}library/fnmatch.html",  # Unix filename pattern matching
    f"{base_url}library/linecache.html",  # Random access to text lines
    f"{base_url}library/shutil.html",  # High-level file operations
    
    # ==================== DATA PERSISTENCE ====================
    f"{base_url}library/pickle.html",  # Python object serialization
    f"{base_url}library/copyreg.html",  # Register pickle support functions
    f"{base_url}library/shelve.html",  # Python object persistence
    f"{base_url}library/marshal.html",  # Internal Python object serialization
    f"{base_url}library/dbm.html",  # Interfaces to Unix databases
    f"{base_url}library/sqlite3.html",  # SQLite database
    
    # ==================== DATA COMPRESSION & ARCHIVING ====================
    f"{base_url}library/zlib.html",  # Compression compatible with gzip
    f"{base_url}library/gzip.html",  # Support for gzip files
    f"{base_url}library/bz2.html",  # Support for bzip2 compression
    f"{base_url}library/lzma.html",  # Compression using LZMA algorithm
    f"{base_url}library/zipfile.html",  # Work with ZIP archives
    f"{base_url}library/tarfile.html",  # Read and write tar archive files
    
    # ==================== FILE FORMATS ====================
    f"{base_url}library/csv.html",  # CSV file reading and writing
    f"{base_url}library/configparser.html",  # Configuration file parser
    f"{base_url}library/tomllib.html",  # Parse TOML files
    f"{base_url}library/netrc.html",  # netrc file processing
    f"{base_url}library/plistlib.html",  # Property list files
    
    # ==================== CRYPTOGRAPHIC SERVICES ====================
    f"{base_url}library/hashlib.html",  # Secure hashes and message digests
    f"{base_url}library/hmac.html",  # Keyed-hashing for message authentication
    f"{base_url}library/secrets.html",  # Generate secure random numbers
    
    # ==================== OPERATING SYSTEM ====================
    f"{base_url}library/os.html",  # Miscellaneous operating system interfaces
    f"{base_url}library/io.html",  # Core tools for working with streams
    f"{base_url}library/time.html",  # Time access and conversions
    f"{base_url}library/argparse.html",  # Parser for command-line options
    f"{base_url}library/getopt.html",  # C-style parser for command line options
    f"{base_url}library/logging.html",  # Logging facility
    f"{base_url}library/logging.config.html",  # Logging configuration
    f"{base_url}library/logging.handlers.html",  # Logging handlers
    f"{base_url}library/getpass.html",  # Portable password input
    f"{base_url}library/curses.html",  # Terminal handling for character-cell displays
    f"{base_url}library/platform.html",  # Access to underlying platform data
    f"{base_url}library/errno.html",  # Standard errno system symbols
    f"{base_url}library/ctypes.html",  # Foreign function library
    
    # ==================== CONCURRENT EXECUTION ====================
    f"{base_url}library/threading.html",  # Thread-based parallelism
    f"{base_url}library/multiprocessing.html",  # Process-based parallelism
    f"{base_url}library/multiprocessing.shared_memory.html",  # Shared memory
    f"{base_url}library/concurrent.html",  # Concurrent execution
    f"{base_url}library/concurrent.futures.html",  # Launching parallel tasks
    f"{base_url}library/subprocess.html",  # Subprocess management
    f"{base_url}library/sched.html",  # Event scheduler
    f"{base_url}library/queue.html",  # Synchronized queue class
    f"{base_url}library/contextvars.html",  # Context variables
    f"{base_url}library/_thread.html",  # Low-level threading API
    
    # ==================== ASYNCIO ====================
    f"{base_url}library/asyncio.html",  # Asynchronous I/O
    f"{base_url}library/asyncio-task.html",  # Coroutines and Tasks
    f"{base_url}library/asyncio-stream.html",  # Streams
    f"{base_url}library/asyncio-sync.html",  # Synchronization primitives
    f"{base_url}library/asyncio-subprocess.html",  # Subprocesses
    f"{base_url}library/asyncio-queue.html",  # Queues
    f"{base_url}library/asyncio-exceptions.html",  # Exceptions
    f"{base_url}library/asyncio-eventloop.html",  # Event loop
    f"{base_url}library/asyncio-protocol.html",  # Protocols
    f"{base_url}library/asyncio-policy.html",  # Policies
    f"{base_url}library/asyncio-platforms.html",  # Platform support
    
    # ==================== NETWORKING ====================
    f"{base_url}library/socket.html",  # Low-level networking interface
    f"{base_url}library/ssl.html",  # TLS/SSL wrapper for socket objects
    f"{base_url}library/select.html",  # Waiting for I/O completion
    f"{base_url}library/selectors.html",  # High-level I/O multiplexing
    f"{base_url}library/signal.html",  # Set handlers for asynchronous events
    f"{base_url}library/mmap.html",  # Memory-mapped file support
    
    # ==================== INTERNET DATA ====================
    f"{base_url}library/email.html",  # Email and MIME handling package
    f"{base_url}library/json.html",  # JSON encoder and decoder
    f"{base_url}library/mailbox.html",  # Manipulate mailboxes
    f"{base_url}library/mimetypes.html",  # Map filenames to MIME types
    f"{base_url}library/base64.html",  # Base16, Base32, Base64 encoding
    f"{base_url}library/binascii.html",  # Binary/ASCII conversions
    f"{base_url}library/quopri.html",  # Encode/decode MIME quoted-printable
    
    # ==================== HTML & XML ====================
    f"{base_url}library/html.html",  # HTML support
    f"{base_url}library/html.parser.html",  # Simple HTML parser
    f"{base_url}library/html.entities.html",  # HTML entity definitions
    f"{base_url}library/xml.html",  # XML processing modules
    f"{base_url}library/xml.etree.elementtree.html",  # ElementTree XML API
    f"{base_url}library/xml.dom.html",  # DOM API
    f"{base_url}library/xml.dom.minidom.html",  # Minimal DOM implementation
    f"{base_url}library/xml.sax.html",  # SAX2 parser
    
    # ==================== INTERNET PROTOCOLS ====================
    f"{base_url}library/webbrowser.html",  # Web browser controller
    f"{base_url}library/urllib.html",  # URL handling modules
    f"{base_url}library/urllib.request.html",  # Extensible library for opening URLs
    f"{base_url}library/urllib.response.html",  # Response classes
    f"{base_url}library/urllib.parse.html",  # Parse URLs
    f"{base_url}library/urllib.error.html",  # Exception classes
    f"{base_url}library/urllib.robotparser.html",  # Parser for robots.txt
    f"{base_url}library/http.html",  # HTTP modules
    f"{base_url}library/http.client.html",  # HTTP protocol client
    f"{base_url}library/ftplib.html",  # FTP protocol client
    f"{base_url}library/poplib.html",  # POP3 protocol client
    f"{base_url}library/imaplib.html",  # IMAP4 protocol client
    f"{base_url}library/smtplib.html",  # SMTP protocol client
    f"{base_url}library/uuid.html",  # UUID objects
    f"{base_url}library/socketserver.html",  # Framework for network servers
    f"{base_url}library/http.server.html",  # HTTP servers
    f"{base_url}library/http.cookies.html",  # HTTP state management
    f"{base_url}library/http.cookiejar.html",  # Cookie handling
    f"{base_url}library/xmlrpc.html",  # XML-RPC server and client modules
    f"{base_url}library/xmlrpc.client.html",  # XML-RPC client
    f"{base_url}library/xmlrpc.server.html",  # XML-RPC server
    f"{base_url}library/ipaddress.html",  # IPv4/IPv6 manipulation
    
    # ==================== MULTIMEDIA ====================
    f"{base_url}library/wave.html",  # Read and write WAV files
    f"{base_url}library/colorsys.html",  # Color system conversions
    
    # ==================== INTERNATIONALIZATION ====================
    f"{base_url}library/gettext.html",  # Multilingual internationalization services
    f"{base_url}library/locale.html",  # Internationalization services
    
    # ==================== PROGRAM FRAMEWORKS ====================
    f"{base_url}library/turtle.html",  # Turtle graphics
    f"{base_url}library/cmd.html",  # Line-oriented command interpreter
    f"{base_url}library/shlex.html",  # Simple lexical analysis
    
    # ==================== GUI ====================
    f"{base_url}library/tkinter.html",  # Tkinter GUI
    f"{base_url}library/tkinter.colorchooser.html",
    f"{base_url}library/tkinter.font.html",
    f"{base_url}library/tkinter.messagebox.html",
    f"{base_url}library/tkinter.scrolledtext.html",
    f"{base_url}library/tkinter.ttk.html",  # Themed widgets
    
    # ==================== DEVELOPMENT TOOLS ====================
    f"{base_url}library/typing.html",  # Type hints support
    f"{base_url}library/pydoc.html",  # Documentation generator
    f"{base_url}library/doctest.html",  # Test interactive examples
    f"{base_url}library/unittest.html",  # Unit testing framework
    f"{base_url}library/unittest.mock.html",  # Mock object library
    f"{base_url}library/test.html",  # Regression tests
    f"{base_url}library/venv.html",  # Virtual environments
    
    # ==================== DEBUGGING & PROFILING ====================
    f"{base_url}library/bdb.html",  # Debugger framework
    f"{base_url}library/faulthandler.html",  # Dump Python traceback
    f"{base_url}library/pdb.html",  # Python debugger
    f"{base_url}library/profile.html",  # Python profilers
    f"{base_url}library/timeit.html",  # Measure execution time
    f"{base_url}library/trace.html",  # Trace Python statement execution
    f"{base_url}library/tracemalloc.html",  # Trace memory allocations
    
    # ==================== RUNTIME SERVICES ====================
    f"{base_url}library/sys.html",  # System-specific parameters and functions
    f"{base_url}library/sysconfig.html",  # Python configuration
    f"{base_url}library/builtins.html",  # Built-in objects
    f"{base_url}library/__main__.html",  # Top-level script environment
    f"{base_url}library/warnings.html",  # Warning control
    f"{base_url}library/dataclasses.html",  # Data classes
    f"{base_url}library/contextlib.html",  # Context manager utilities
    f"{base_url}library/abc.html",  # Abstract base classes
    f"{base_url}library/atexit.html",  # Exit handlers
    f"{base_url}library/traceback.html",  # Print or retrieve stack traceback
    f"{base_url}library/__future__.html",  # Future statement definitions
    f"{base_url}library/gc.html",  # Garbage collector
    f"{base_url}library/inspect.html",  # Inspect live objects
    f"{base_url}library/site.html",  # Site-specific configuration
    
    # ==================== CUSTOM INTERPRETERS ====================
    f"{base_url}library/code.html",  # Interpreter base classes
    f"{base_url}library/codeop.html",  # Compile Python code
    
    # ==================== IMPORTING MODULES ====================
    f"{base_url}library/zipimport.html",  # Import modules from ZIP archives
    f"{base_url}library/pkgutil.html",  # Package extension utility
    f"{base_url}library/modulefinder.html",  # Find modules
    f"{base_url}library/runpy.html",  # Locate and run Python modules
    f"{base_url}library/importlib.html",  # Import machinery
    f"{base_url}library/importlib.resources.html",  # Resource reading
    f"{base_url}library/importlib.metadata.html",  # Accessing package metadata
    
    # ==================== PYTHON LANGUAGE SERVICES ====================
    f"{base_url}library/ast.html",  # Abstract syntax trees
    f"{base_url}library/symtable.html",  # Access to compiler's symbol tables
    f"{base_url}library/token.html",  # Constants for Python parse trees
    f"{base_url}library/keyword.html",  # Test for Python keywords
    f"{base_url}library/tokenize.html",  # Tokenizer for Python source
    f"{base_url}library/tabnanny.html",  # Indentation validator
    f"{base_url}library/pyclbr.html",  # Python module browser support
    f"{base_url}library/py_compile.html",  # Compile Python source files
    f"{base_url}library/compileall.html",  # Byte-compile Python libraries
    f"{base_url}library/dis.html",  # Disassembler for Python bytecode
    f"{base_url}library/pickletools.html",  # Tools for pickle developers
    
    # ==================== WINDOWS SPECIFIC ====================
    f"{base_url}library/msvcrt.html",  # Useful routines from MS VC++ runtime
    f"{base_url}library/winreg.html",  # Windows registry access
    f"{base_url}library/winsound.html",  # Sound-playing interface for Windows
    
    # ==================== UNIX SPECIFIC ====================
    f"{base_url}library/posix.html",  # Most common POSIX system calls
    f"{base_url}library/pwd.html",  # Password database
    f"{base_url}library/grp.html",  # Group database
    f"{base_url}library/termios.html",  # POSIX style tty control
    f"{base_url}library/tty.html",  # Terminal control functions
    f"{base_url}library/pty.html",  # Pseudo-terminal utilities
    f"{base_url}library/fcntl.html",  # fcntl and ioctl system calls
    f"{base_url}library/resource.html",  # Resource usage information
    f"{base_url}library/syslog.html",  # Unix syslog library routines
    
    # ==================== SUPERSEDED MODULES ====================
    f"{base_url}library/optparse.html",  # Parser for command line options (use argparse)
    f"{base_url}library/imp.html",  # Access import internals (deprecated)
    
    # ==================== REFERENCE ====================
    f"{base_url}reference/index.html",
    f"{base_url}reference/introduction.html",
    f"{base_url}reference/lexical_analysis.html",
    f"{base_url}reference/datamodel.html",  # Data model (important!)
    f"{base_url}reference/executionmodel.html",
    f"{base_url}reference/import.html",  # Import system
    f"{base_url}reference/expressions.html",  # Expressions
    f"{base_url}reference/simple_stmts.html",  # Simple statements
    f"{base_url}reference/compound_stmts.html",  # Compound statements (if, for, while, etc.)
    f"{base_url}reference/toplevel_components.html",
    
    # ==================== HOWTOS ====================
    f"{base_url}howto/index.html",
    f"{base_url}howto/pyporting.html",  # Porting Python 2 to 3
    f"{base_url}howto/cporting.html",  # Porting C extensions
    f"{base_url}howto/curses.html",  # Curses programming
    f"{base_url}howto/descriptor.html",  # Descriptors
    f"{base_url}howto/functional.html",  # Functional programming
    f"{base_url}howto/logging.html",  # Logging
    f"{base_url}howto/logging-cookbook.html",  # Logging cookbook
    f"{base_url}howto/regex.html",  # Regular expressions
    f"{base_url}howto/sockets.html",  # Socket programming
    f"{base_url}howto/sorting.html",  # Sorting
    f"{base_url}howto/unicode.html",  # Unicode
    f"{base_url}howto/urllib2.html",  # urllib.request
    f"{base_url}howto/argparse.html",  # Argparse tutorial
    f"{base_url}howto/ipaddress.html",  # ipaddress module
    f"{base_url}howto/clinic.html",  # Argument Clinic
    f"{base_url}howto/instrumentation.html",  # Instrumentation
    f"{base_url}howto/perf_profiling.html",  # Performance profiling
    f"{base_url}howto/annotations.html",  # Annotations best practices
    f"{base_url}howto/isolating-extensions.html",  # Isolating extension modules
    
    # ==================== FAQ ====================
    f"{base_url}faq/index.html",
    f"{base_url}faq/general.html",
    f"{base_url}faq/programming.html",
    f"{base_url}faq/design.html",
    f"{base_url}faq/library.html",
    f"{base_url}faq/extending.html",
    f"{base_url}faq/windows.html",
    f"{base_url}faq/gui.html",
    ]
    documents = []
    for url in important_urls:
        if url in visited_urls:
            continue
        print(f'Scraping: {url}')
        doc = parse_url(url)
        if doc and doc['content']:
            documents.append(doc)
            visited_urls.add(url)
        time.sleep(0.5)

    return documents

def save_documents(documents):
    output_file = output_dir / 'python_docs.json'
    with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(documents)} documents to {output_file}")
    return output_file

def main():
    documents = scrape_all_sections()
    output_file = save_documents(documents)
    print(f'saved to: {output_file}')

if __name__ == main():
    main()